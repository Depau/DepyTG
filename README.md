# DepyTG

The only Python3 Telegram bot library that does *nothing*.

### Wait, what?

Well of course it doesn't actually do *nothing* at all. However, it does nothing compared to many other Telegram bot libraries, and that's a design goal.

### Design goals

The main goal is to KISS — Keep It Simple, Stupid.

Other than being simple, DepyTG tries to:

 - Have a 1:1 correspondence with Telegram's official API specs
 - Be compatible with any *network* library you may want to use — Requests, Flask, JSON+Urllib\*, anything
 - Make sure 99.9999% of its objects are JSON-serializable
 - Provide a simple (but totally optional) API to do the network stuff
 - Heavily integrate with IDEs that support code insights by type-hinting everything that can be type-hinted
 
 
 # Big note
 
 This is a work in progress! I wrote this from scratch to write my own Telegram bots. I haven't tested it very much. I'll test it as I work on them. I'll write some tests and add CI soon.
 
 
 ### Possible questions
 
 ##### Why the hell did you define *every* possible object in the API?
 
 Because one of my goals was to have code completion.
 
 All Telegram API objects and methods are children of `TelegramObjectBase`, which is a subclass of `dict`. This means everything (except for `InputFile`) is JSON-serializable and can be used outside of this library.
 
 `dict` has been extended to check field types and to access them with the standard dot notation, so that IDEs like PyCharm can warn you if you do something wrong.
 
 The reason they were "rewritten" is to allow for type checking.