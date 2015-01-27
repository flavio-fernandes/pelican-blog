Title: Use .ssh/authorized_keys to block inadvertent username
Date: 2015-01-22 10:10
Author: flavio
Category: Hacks
Tags: config, ssh
Slug: login-as-user-bla

Nice hack in .ssh/authorized_keys to stop unwanted username from logging in

<!--more-->

This is a nice hack you can do to so that you don't waste time typing
**ssh** command only to realize you used the wrong username.

I find it useful when I omit the *user@* portion in the ssh command,
thinking that the id locally used is the same as the one I should be
using in the remote system.

All you need to do is to prepend the line(s) in the
~wrong-username/.ssh/authorized_keys with the following string:

    no-port-forwarding,no-agent-forwarding,no-X11-forwarding,command="echo 'Re-login as \"xyz\".';echo;sleep 5" 

You just need to put that string right before each line, which would normally begin with **ssh-rsa**.
Lastly, make sure to have a space between the added string above and the beginning of the
line (i.e. **ssh-rsa**).

Enjoy!
