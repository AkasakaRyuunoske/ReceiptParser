***0.6.9***
- minor cleaning

***0.6.8***
- Added onclick header change location to /
- Changed input boxes for reference dates, store and notest to have correct sizes and backgrounds on receipt_card
- Changed model selection box to have correct background
- Changed index

***0.6.6***
- Changes to the receipt form

***0.6.5***
- Changed receipt card adding new button to submit
- Changed image and receipt forms to be single form
- Added new models to manage the old separation

- ***0.6.4***
- Added full glitch text effect css

***0.6.3***
- Added input fields to receipt card
- Added inference scripts to add_receipt_page

***0.6.2***
- Changed layout of add receipt page
- Changed image upload logic
***0.6.1***
- Added tailwindcss
- Added initial code for receipt card

***0.6.0***
- Added base html component
- Added navbar
- Added receipts page
- Added receipts storage page
- Added add receipt page
- Added add model input overview html component
- Added settings page
- Added dashboard page
- Added ui figma design

***0.5.0***
- Added icon to browser tab
- Added service to handle receipt inserting logic
- Added pretty print of inserted receipts
- Changed item_name to no longer have UNIQUE constraint 
- Changed city to no longer have UNIQUE constraint 
- Changed save receipt logic to use v0_3 db e-r
- Changed original_image_path field to ImageField type

***0.4.3***
- Added application icon (placeholder)

***0.4.2***
- Added new ReceiptItems model

***0.4.1***
- Added view of inserted Receipts
- Added a condition to reduce useless interferences on the model

***0.4.0***
- Added __str__ methods to all models
- Added insert of inference results
- Added E-R diagram ver 0_2

***0.3.1***
- Added separate files for prompt and json schema

***0.3.0***
- Added minimal usable front-end
- Added Upload -> Inference -> Display workflow working
- Added model's output as stream into fe
- Changed patchnotes format to MAJOR.MINOR.PATCH structure as per [keepchangelog](https://keepachangelog.com/en/1.1.0/)
- Changed name from patch-notes.md -> CHANGELOG.md

***0.2.0***
- Added django infrastructure
- Added file upload
- Added support for English Text MT (crucial)

***0.1.0***
- Added database design that includes entities: Receipts, Items, Stores, Payment Methods, Item Categories, Store Names
- Added mock of input workflow
- Added patch-notes 