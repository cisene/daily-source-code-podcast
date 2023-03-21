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
 