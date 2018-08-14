import sys

__all__ = ['PY2', 'input', 'StringIO', 'BytesIO', 'ConfigParser', 'u']

PY2 = sys.version_info[0] < 3

if PY2:
    input = raw_input

    try:
        import cStringIO

        StringIO = cStringIO.StringIO
    except ImportError:
        import StringIO

        StringIO = StringIO.StringIO

    BytesIO = StringIO

    import ConfigParser
    ConfigParser = ConfigParser

    def u(s, encoding='utf8'):
        """
        Cast bytes or unicode to unicode

        :param s: unicode or bytes
        :type s: bytearray or str
        """
        if isinstance(s, str):
            try:
                return s.decode(encoding, errors='replace')
            except:
                return str(s)
        elif isinstance(s, unicode):
            return s
        elif isinstance(s, buffer):
            try:
                return s.decode(encoding, errors='replace')
            except:
                return str(s)
        else:
            raise TypeError("Expected unicode or bytes, got %r" % s)

else:

    input = input

    import io
    StringIO = io.StringIO
    BytesIO = io.BytesIO

    import configparser
    ConfigParser = configparser

    def u(s, encoding='utf8'):
        """
        Cast bytes or unicode to unicode

        :param s: unicode or bytes
        :type s: bytearray or str
        """
        if isinstance(s, bytes):
            try:
                return s.decode(encoding, errors='replace')
            except:
                return str(s)
        elif isinstance(s, str):
            return s
        else:
            raise TypeError("Expected unicode or bytes, got %r" % s)
