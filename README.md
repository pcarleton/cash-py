# CashCoach

A personal finance coach that pulls in financial data you sync using Plaid.io and sends periodic reminder slack messages and creates google sheets reports.

# Why?
I used Mint and Level Money to track my spending, but I was unsatisfied.  I have two quirks to my financial situation: 1. I collect rent and pay the landlord for both members of my apartment and 2. I have a shared credit card where most of the transactions are split.  Unfortunately, Mint and Level Money are not well-equipped to deal with these situations.  I want to be able to ask questions like: How much money did I spend last week?  Or, based on how much I have spent so far this month, how much can I comfortably spend this weekend?

# How?
Plaid.io does the heavy-lifting of syncing the financial data from multiple accounts.  I wanted both to be able to pull information from my system by asking questions, and also for it to push information to me, for instance on Friday afternoon when I’m making plans for the weekend so I can decide what kind of weekend to have.   For this reason, I decided a chatbot was a good fit.

I also did not want my analysis to be limited to a conversational interface.  For deeper analysis, I am most comfortable in a spreadsheet, so I also added the ability to sync the data to Google Sheets.

# What's Next?

Currently I run the code on a RaspberryPi with several cron-jobs to handle syncing the Google Sheets report as well as send me weekly and monthly spending updates.  My next priority is to make the application support multiple users in order to share it more broadly
