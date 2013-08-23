hg-hipchat-hook-py
==================

This is a script to hook up your Mercurial (Hg) repo to a HipChat room.

PayScale runs our Hg server on Windows and when we started using HipChat, I noticed that
there was only a BASH integration. It seemed pretty obvious that there should be a Python
one, but I couldn't find it.

This has definitely been an exercise in learning the Mercurial API. I didn't know anything
before, and I still don't. I just copied and pasted stuff until it worked.

Example Output to HipChat
-------------------------
![screenshot of script output to hipchat](http://www.payscale.com/cms-images/default-source/screenshots/screen-shot-2013-08-23-at-11-50-10-am.png?sfvrsn=2)

The following things are linked:

 * `# revisions` linked to the "shortlog"
 * `[#]` link to the specific revision
 
To Install
----------

You really only need this script on one machine, and it will be your centralized server.

Clone this repo:

    git clone git@github.com:adamb0mb/hg-hipchat-hook-py.git
    
Configure your `.hg/hgrc`

	[hooks]
	changegroup = python:c:\git\hg-hipchat-hook-py\hg-hipchat-hook-py.py:hook
	
	[hipchat]
	branches='default,staging'
	web="http://yourserver:8000"
	staging_api_key=a1b2c3d4e5f67890
	staging_room_id = 123
	default_api_key=a1b2c3d4e5f67890
	default_room_id = 124

#### Explanation of `.hg/hgrc` parameters ####
 * The `hooks` section has lot of different things you can hook up to, but this script only supports 'changegroup'
 * the `hipchat` section is all of the parameters for this script
  * `branches` are the branches you want to watch, in a comma separated list
  * `web` is the base web url of the mercurial server
  * `*_api_key` You need an entry for every branch you've specified in the `branches` parameter.
   * It only needs 'notification' permissions
   * You can create a new API key here: `http://<your>.hipchat.com/admin/api`
  * `*_room_id` is the room in HipChat you want to send the message to.
   * This is the "API ID"
   * You can find the API by going here, and clicking on the room you want: `http://<your>.hipchat.com/admin/rooms`
