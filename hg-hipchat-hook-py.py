# -*- coding: utf-8 -*-
"""
Mercurial to HipChat changegroup hook in python

Created on Mon Aug 19 10:22:26 2013
@author: Adam Phillabaum <adamp@payscale.com>
"""

import re
import urllib
import urllib2
from mercurial.node import *

def message_room(url, token, parameters, notify=False):
    """Sens a message to the specified HipChat room
    
    I was having issues using python_simple_hipchat library on windows 
    (something about the json library), so I copied the important stuff here
    But, you shold use this: https://github.com/kurttheviking/python-simple-hipchat
    """
    base_hipchat_url = "https://api.hipchat.com/v1/"

    query_parameters = dict()
    query_parameters['auth_token'] = token
    query_string = urllib.urlencode(query_parameters)
    request_data = urllib.urlencode(parameters)

    method_url = base_hipchat_url + url + '?' + query_string
    req = urllib2.Request(method_url, request_data)
    urllib2.urlopen(req)
            
def clean_user(user,return_html=False):
    """ Clean up the user string

    THIS FUNCTION IS FAR FROM DONE! It is totally going to blow up if it gets a
    poorly formatted user string.
    The string given from can very dirty. This helps clean it up to be
    HipChat friendly when we print the message.
    
    Args:
        user: the ctx.user() string from the mercurial change context.
        return_html: boolean about what the return string should look like.
    
    Returns:
        either an HTML string linking the name to the email address, or just
        a plain string with the name.
        If the regex can't parse the name and email, it just returns back the
        input
    """
    re_user_and_email = re.compile('(.+)\s<(.+)>')
    m = re_user_and_email.match(user)
    if (m):
        if (return_html):
            return "<a href='mailto:{email}'>{name}</a>".format(
                    email=m.group(2),
                    name=m.group(1))
        else:
            return m.group(1)
    else:
        return user

def hook(ui, repo, hooktype, node=None, **kwargs):
    """The hook to be called from Mercurial on "chanegroup"
    
    This is the meat of this script. It processes the hook, builds the text,
    and chats the message to HipChat
    
    Args:
        ui: the ui variable passed in from Hg
        repo: the repo variable passed in from Hg
        hooktype: the type of hook that is callingthis. We only suport 'changegroup'
        node: basically, this is the revision that is being checked in
        **kwargs: a random grabback of other variabe that may be passed in by Hg
    """

    ui.debug("Hg-->HipChat Hook invoked with {hooktype}\n".format(hooktype=hooktype))    
    
    # Error loud. Error Proud.                                                      
    if (hooktype != 'changegroup'):
        ui.warn("Someone has the hg-hipchat-hook-py extension configured for {hooktype}, an event other than 'changegroup', you should fix it.\n".format(hooktype=hooktype))
        return -1

    # Pulling in some of the basic config entries
    monitored_repos = ui.configlist('hipchat','branches')    
    if (not monitored_repos):
        ui.warn("No repos to monitor in .hg/hgrc\n")
        return -1
    url_for_web_hg = ui.config('hipchat','web')
    if (not url_for_web_hg):
        ui.warn("Base URL for changes not configured in .hg/hgrc\n")
        return -1
    
    # Our change contect is the key to everything. It hass all the juicy info
    ctx = repo.changectx(node)
    
    # branch filtering
    branch = ctx.branch()
    if (branch not in monitored_repos):
        ui.debug("no branches matches from repos in config: \n")
        for monitored_repo in monitored_repos:
            ui.debug(monitored_repo+" ")
        return 0

    # get branch specific config variable from .hg/hgrc
    hipchat_token = ui.config('hipchat',branch+'_api_key')
    hipchat_room_id = ui.config('hipchat',branch+'_room_id')
    if (not hipchat_room_id or not hipchat_token):
        ui.warn("Unable to get the HipChat config options for this {branch} branch".format(branch=branch))
        return -1

    # Build up the main subcomponents of the message
    start = repo.changelog.rev(bin(node))
    end = len(repo.changelog)
    url_for_web_hg_shortlog = url_for_web_hg+"/shortlog/"
    url_for_web_hg_revision = url_for_web_hg+"/rev/"

    linkToHttp = "{0}{1}?revcount={2}".format(url_for_web_hg_shortlog,str(end-1),end-start)
    user = clean_user(ctx.user(),False)

    # Example string built: Adam Phillabaum push [2 revisions](link) to consumer branch
    text_message = "{user} pushed <a href='{link}'>{numRevisions} revisions</a> to {branch} branch<br />".format(
                link=linkToHttp,
                user=user,
                numRevisions=end-start,
                branch=branch) 

    # print descriptions for each commmit with link to the individual commit
    text_message = text_message + "<ul>"
    if (end-start > 5):
        short_start = end-5
    else:
        short_start = start
    for rev in xrange(short_start, end):
        revNode = repo.changelog.node(rev)
        revCtx = repo.changectx(revNode)
        text_message = "{prev} <li>[<a href='{linkToRev}'>{rev}</a>] {description}</li>>".format(
                        prev=text_message,
                        linkToRev=url_for_web_hg_revision+str(revCtx),
                 
                 rev=revCtx.rev(),
                        description=revCtx.description())
    text_message = text_message + "</ul>"
    
    # push our message out
    message_room('rooms/message',
               token=hipchat_token,
               parameters={
                   'room_id': hipchat_room_id, 
                   'from': 'pshg', 
                   'message': text_message,
                   'message_format': 'html'})