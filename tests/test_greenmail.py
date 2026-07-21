from imap_tools import MailBoxUnencrypted


def test_seeded_inbox_has_all_fixture_messages(greenmail_mailbox: MailBoxUnencrypted):
    assert len(greenmail_mailbox.uids()) == 12
