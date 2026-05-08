# kule-liveblog-bot
This Discord bot is meant to support the Philippine Collegian's live blog operations. It can:
1. Create Google Sheet files based on forum posts in the coverages forum.
2. Automatically update the Sheet with messages that are sent in the forum post.

The general flow is as follows:
1. A writer creates a forum post in the coverages forum that is solely for messages that will be edited and later posted on 24liveblog.
2. Automatically, the forum post leads to a Google Sheet file created in the Collegian's Drive, with a name that contains the forum post name.
3. When a writer sends a message in the forum post, a new row is added to the Google Sheet.
4. The editor edits the message in the Google Sheet.
5. Once done, someone doing the live blog manually posts the message in the Google Sheet.