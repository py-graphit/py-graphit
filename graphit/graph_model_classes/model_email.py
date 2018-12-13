# -*- coding: utf-8 -*-

"""
file: model_email.py

Graph model classes for dealing with emails

TODO: checkout https://github.com/JoshData/python-email-validator/blob/master/email_validator/__init__.py
      for IDN emails
"""

import re
import logging
import smtplib

from graphit import __module__
from graphit.graph_mixin import NodeEdgeToolsBaseClass

__all__ = ['Email']
logger = logging.getLogger(__module__)

try:
    import dns.resolver
except ImportError:
    logger.warning('Email address DNS and mailbox verification requires the "dnspython" module. Not installed')

RFC_EMAIL_REGEX = r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$'


class Email(NodeEdgeToolsBaseClass):

    def set(self, key, value=None, **kwargs):
        """
        Validate email adress syntax according to the 'addr-spec' part of the
        RFC 2822 specification.
        """

        if key == self.value_tag:
            if re.match(RFC_EMAIL_REGEX, value) is None:
                logger.error('Invalid email adress syntax: {0}'.format(value))
                return

        self.nodes[self.nid][key] = value

    def validate_existence(self, timeout=10):
        """
        Email DNS and mailbox verification.

        This method requires dnspython module to be installed

        Incorrect results: some mail servers will give you incorrect results,
        for instance catch-all servers, which will accept all incoming email
        addresses, often forwarding incoming emails to a central mailbox.
        Yahoo addresses displays this catch-all behavior.

        .. warning:: Using this method allot will risk blacklisting your IP
                     (e.g. Spamhaus), especially if you are using a dynamic IP
                     address from your ISP.

        :param timeout: SMTP timeout in seconds
        :type timeout:  :py:int
        """

        email = self.get()
        if email:

            # Get domain for DNS lookup
            splitAddress = email.split('@')
            domain = str(splitAddress[1])

            # MX record lookup
            records = dns.resolver.query(domain, 'MX')
            mxRecord = str(records[0].exchange)

            # SMTP lib setup (use debug level for full output)
            server = smtplib.SMTP(timeout=timeout)
            server.set_debuglevel(0)

            # SMTP Conversation
            server.connect(mxRecord)
            server.helo(server.local_hostname)
            server.mail('mvd@gmail.com')
            code, message = server.rcpt(str(email))
            server.quit()

            if code == 250:
                return True
            else:
                logging.error('SMTP error {0}: {1}'.format(code, message))

        return False
