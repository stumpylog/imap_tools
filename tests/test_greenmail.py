from imap_tools import MailBoxUnencrypted
from imap_tools.consts import MailMessageFlags
from imap_tools.query import A


def test_seeded_inbox_has_all_fixture_messages(greenmail_mailbox: MailBoxUnencrypted):
    assert len(greenmail_mailbox.uids()) == 12


def test_fetch_returns_all_messages(greenmail_mailbox: MailBoxUnencrypted):
    fetched = list(greenmail_mailbox.fetch(bulk=True, headers_only=True))
    assert len(fetched) == 12


def test_fetch_nonexistent_uid_returns_empty(greenmail_mailbox: MailBoxUnencrypted):
    fetched = list(greenmail_mailbox.fetch(A(uid=['999999']), bulk=True))
    assert len(fetched) == 0


def test_copy_and_move(greenmail_mailbox: MailBoxUnencrypted):
    greenmail_mailbox.folder.create('temp1')
    greenmail_mailbox.folder.create('temp2')

    uids = greenmail_mailbox.uids()
    greenmail_mailbox.copy(uids, 'temp1')
    assert len(greenmail_mailbox.uids()) == 12  # source folder unchanged

    greenmail_mailbox.folder.set('temp1')
    assert len(greenmail_mailbox.uids()) == 12

    greenmail_mailbox.move(greenmail_mailbox.uids(), 'temp2')
    assert len(greenmail_mailbox.uids()) == 0

    greenmail_mailbox.folder.set('temp2')
    assert len(greenmail_mailbox.uids()) == 12


def test_flag_and_delete(greenmail_mailbox: MailBoxUnencrypted):
    uids = greenmail_mailbox.uids()
    greenmail_mailbox.flag(uids, MailMessageFlags.FLAGGED, True)
    fetched = list(greenmail_mailbox.fetch(bulk=True, headers_only=True))
    assert all(MailMessageFlags.FLAGGED in msg.flags for msg in fetched)

    greenmail_mailbox.delete(uids)
    assert len(greenmail_mailbox.uids()) == 0


def test_append(greenmail_mailbox: MailBoxUnencrypted):
    message = (
        b'From: Test <test@example.com>\n'
        b'To: Dest <dest@example.com>\n'
        b'Subject: greenmail append test\n'
        b'Content-Type: text/plain; charset=US-ASCII\n\n'
        b'Body text.\n'
    )
    before = len(greenmail_mailbox.uids())
    greenmail_mailbox.append(message, folder='INBOX')
    greenmail_mailbox.folder.set('INBOX')
    after = len(greenmail_mailbox.uids())
    assert after == before + 1


def test_copy_move_flag_delete_with_chunks(greenmail_mailbox: MailBoxUnencrypted):
    greenmail_mailbox.folder.create('chunked1')
    greenmail_mailbox.folder.create('chunked2')

    uids = greenmail_mailbox.uids()
    greenmail_mailbox.copy(uids, 'chunked1', chunks=4)
    greenmail_mailbox.folder.set('chunked1')
    assert len(greenmail_mailbox.uids()) == 12

    greenmail_mailbox.move(greenmail_mailbox.uids(), 'chunked2', chunks=4)
    assert len(greenmail_mailbox.uids()) == 0

    greenmail_mailbox.folder.set('chunked2')
    chunked_uids = greenmail_mailbox.uids()
    assert len(chunked_uids) == 12

    greenmail_mailbox.flag(chunked_uids, MailMessageFlags.FLAGGED, True, chunks=4)
    fetched = list(greenmail_mailbox.fetch(bulk=True, headers_only=True))
    assert all(MailMessageFlags.FLAGGED in msg.flags for msg in fetched)

    greenmail_mailbox.delete(chunked_uids, chunks=4)
    assert len(greenmail_mailbox.uids()) == 0
