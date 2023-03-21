# iPod - The script that started everything

The little script that started it all, Adam Curry's experimentation of copying or synch'ing downloaded podcast episodes onto his iPod. His experiments eventually snowballed into something bigger ...



## The Zipfile

The zipfile was found while parsing an [RSS example file](https://cyber.harvard.edu/rss/examples/rssEnclosuresExample.xml) while looking for bits and pieces for [Daily Source Code Restoration project](https://github.com/cisene/daily-source-code-podcast), as one enclosure stood out among the others and had a different mime-type, "application/zip".

```xml
<item>
	<title>RSS2iPod</title>
	<description>Mac users can use this <a href="http://radio.weblogs.com/0001014/gems/iPod.zip">folder applescript</a> to automagically update your iPod with any new mp3's that are downloaded to your "Radio UserLand" enclosures folder from <a href="http://www.thetwowayweb.com/payloadsforrss">enclosure aware</a> "rss" feeds. To install: replace "<i>Adam's Curry's iPod"</i> with the name of your iPod and attach the script to your Enclosures folder (located in your Radio UserLand application folder) using the <i>Attach Script To Folder</i> script, located in your <i>/Library/Scripts/Folder Actions/</i> folder. You can test this script by subscribing to the <a href="http://radio.weblogs.com/0001014/categories/syncpod/rss.xml">syncPod channel</a>, which delivers a new mp3 every day. <i>Update</i>: Hmmm, it seems the script only works when the first enclosure is downloaded. Any scripting guru's out there want to help with this script so it transfers <i>all</i> enclosures?</description>
	<guid isPermaLink="false">http://radio.weblogs.com/0001014/categories/payload/2003/10/12.html#a4604</guid>
	<pubDate>Sun, 12 Oct 2003 10:11:34 GMT</pubDate>
	<enclosure url="http://radio.weblogs.com/0001014/gems/iPod.zip" length="1166" type="application/zip"/>
</item>
```

As the original webhost radio.weblogs.com was no longer available but another one with a very similar name and contents, a little adjustment of the URL,  [http://radio-weblogs.com/0001014/gems/iPod.zip](http://radio-weblogs.com/0001014/gems/iPod.zip) and the binary file could be downloaded. The contents of the zipfile is described below, noteworthy is that that the iPod.scpt file inside the zipfile were compressed "13 october, 2003, 15:15".




| Filename  | Description                                  |
| --------- | -------------------------------------------- |
| iPod.scpt | The iPod script in compiled form.            |
| iPod.zip  | A zip-archive containing the iPod.scpt file. |



## The script

A small Applescript of just 21 lines, automated the process of copying the downloaded MP3's onto an iPod, something that wasn't a part of iTunes until much later when Adam had seeded the Apple podcast directory with his OPML collection, but that is a whole other story.

The archived version of the script resurfaced in March of 2023, almost 20 years after it was last compiled.



## Decompiling the compiled scpt-file

While looking around for ways of decompiling the compiled binary, some different packages surfaced and where attempted to decompile the file, without success. Made a request for some help on Mastodon/Fediverse and got responses!

[Mike Neumann](https://podcastindex.social/@mikeneumann) and [BunnyHero](https://podcastindex.social/@bunnyhero@mstdn.ca) both had old Apple machines they could try decompiling the compiled script on, Bunny did get slightly different results due not having iTunes installed, while Mike had iTunes installed and Applescript Editor was able to resolve the dependencies.

**Big thanks to Bunny and Mike for helping out preserving an important piece of history for the future.**




## iPod.applescript - Mike Neumann's version

```applescript
on adding folder items to this_folder after receiving these_items
    -- these_items will contain a list of file references to the added items 
    set item_count to number of items in the these_items
    set addcount to 0
    if item_count is greater than 0 then
        repeat with i from 1 to item_count
            set this_info to info for item i of these_items
            if folder of this_info is false then
                tell application "iTunes.app"
                    «event hookAdd » item i of these_items given «class insh»:«class cPly» "syncPod"
                    addcount = addcount + 1
                end tell
            end if
        end repeat
        if addcount is greater than 0 then
            tell application "iTunes.app"
                «event hookUpdt» "Adam Curry's iPod"
            end tell
        end if
    end if
end adding folder items to
````



## iPod.applescript - BunnyHero's version

```applescript
on adding folder items to this_folder after receiving these_items
	-- these_items will contain a list of file references to the added items 
	set item_count to number of items in the these_items
	set addcount to 0
	if item_count is greater than 0 then
		repeat with i from 1 to item_count
			set this_info to info for item i of these_items
			if folder of this_info is false then
				tell application "iTunes.app"
					«event hookAdd » item i of these_items given «class insh»:«class cPly» "syncPod"
					addcount = addcount + 1
				end tell
			end if
		end repeat
		if addcount is greater than 0 then
			tell application "iTunes.app"
				«event hookUpdt» "Adam Curry's iPod"
			end tell
		end if
	end if
end adding folder items to
```





Created: 2023-03-21 22:25+0100 

Updated: 2023-03-21 22:25+0100
