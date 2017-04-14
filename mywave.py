import struct
import sys
import array
from chunk import Chunk
class Error(Exception):
    pass

WAVE_FORMAT_PCM = 0x0001

_array_fmts = None, 'b', 'h', None, 'i'

def _byteswap3(data):
    ba = bytearray(data)
    ba[::3] = data[2::3]
    ba[2::3] = data[::3]
    return bytes(ba)

class myfile:
    def __init__(self):
        self.buffer=array.array('h')
        self.seek=0
    def write(self,data):
        i=0
        if isinstance(data, basestring):
            #insert_unit=ord(insert_unit)
            temp=array.array('h')
            temp.fromstring(data)
            data=temp
        while i<len(data):
            insert_unit=data[i]
            self.buffer.insert(self.seek,insert_unit)
            i=i+1
            self.seek=self.seek+1
    def seek(self,offset,whence):
        self.seek=offset

    def flush(self):
        self.buffer=[]
        self.seek=0

    def tell(self):
        return self.seek

    def close(self):
        pass

    def get_buffer(self):
        #temp=array.array('h')
        #print self.buffer
        #temp.fromlist(self.buffer)
        '''i=0
        while i<len(self.buffer):
            temp.append(int(self.buffer[i]))'''
        return self.buffer


class Wave_write:
    """Variables used in this class:

    These variables are user settable through appropriate methods
    of this class:
    _file -- the open file with methods write(), close(), tell(), seek()
              set through the __init__() method
    _comptype -- the AIFF-C compression type ('NONE' in AIFF)
              set through the setcomptype() or setparams() method
    _compname -- the human-readable AIFF-C compression type
              set through the setcomptype() or setparams() method
    _nchannels -- the number of audio channels
              set through the setnchannels() or setparams() method
    _sampwidth -- the number of bytes per audio sample
              set through the setsampwidth() or setparams() method
    _framerate -- the sampling frequency
              set through the setframerate() or setparams() method
    _nframes -- the number of audio frames written to the header
              set through the setnframes() or setparams() method

    These variables are used internally only:
    _datalength -- the size of the audio samples written to the header
    _nframeswritten -- the number of frames actually written
    _datawritten -- the size of the audio samples actually written
    """

    def __init__(self):
        self._i_opened_the_file = None
        #if isinstance(f, basestring):
            #f = __builtin__.open(f, 'wb')
        f=myfile()
        self._i_opened_the_file = f
        try:
            self.initfp(f)
        except:
            if self._i_opened_the_file:
                f.close()
            raise

    def initfp(self, file):
        self._file = file
        self._convert = None
        self._nchannels = 0
        self._sampwidth = 0
        self._framerate = 0
        self._nframes = 0
        self._nframeswritten = 0
        self._datawritten = 0
        self._datalength = 0
        self._headerwritten = False

    def __del__(self):
        self.close()

    #
    # User visible methods.
    #
    def setnchannels(self, nchannels):
        if self._datawritten:
            raise Error, 'cannot change parameters after starting to write'
        if nchannels < 1:
            raise Error, 'bad # of channels'
        self._nchannels = nchannels

    def getnchannels(self):
        if not self._nchannels:
            raise Error, 'number of channels not set'
        return self._nchannels

    def setsampwidth(self, sampwidth):
        if self._datawritten:
            raise Error, 'cannot change parameters after starting to write'
        if sampwidth < 1 or sampwidth > 4:
            raise Error, 'bad sample width'
        self._sampwidth = sampwidth

    def getsampwidth(self):
        if not self._sampwidth:
            raise Error, 'sample width not set'
        return self._sampwidth

    def setframerate(self, framerate):
        if self._datawritten:
            raise Error, 'cannot change parameters after starting to write'
        if framerate <= 0:
            raise Error, 'bad frame rate'
        self._framerate = framerate

    def getframerate(self):
        if not self._framerate:
            raise Error, 'frame rate not set'
        return self._framerate

    def setnframes(self, nframes):
        if self._datawritten:
            raise Error, 'cannot change parameters after starting to write'
        self._nframes = nframes

    def getnframes(self):
        return self._nframeswritten

    def setcomptype(self, comptype, compname):
        if self._datawritten:
            raise Error, 'cannot change parameters after starting to write'
        if comptype not in ('NONE',):
            raise Error, 'unsupported compression type'
        self._comptype = comptype
        self._compname = compname

    def getcomptype(self):
        return self._comptype

    def getcompname(self):
        return self._compname

    def setparams(self, params):
        nchannels, sampwidth, framerate, nframes, comptype, compname = params
        if self._datawritten:
            raise Error, 'cannot change parameters after starting to write'
        self.setnchannels(nchannels)
        self.setsampwidth(sampwidth)
        self.setframerate(framerate)
        self.setnframes(nframes)
        self.setcomptype(comptype, compname)

    def getparams(self):
        if not self._nchannels or not self._sampwidth or not self._framerate:
            raise Error, 'not all parameters set'
        return self._nchannels, self._sampwidth, self._framerate, \
              self._nframes, self._comptype, self._compname

    def setmark(self, id, pos, name):
        raise Error, 'setmark() not supported'

    def getmark(self, id):
        raise Error, 'no marks'

    def getmarkers(self):
        return None

    def tell(self):
        return self._nframeswritten

    def writeframesraw(self, data):
        self._ensure_header_written(len(data))
        nframes = len(data) // (self._sampwidth * self._nchannels)
        if self._convert:
            data = self._convert(data)
        if self._sampwidth in (2, 4) and sys.byteorder == 'big':
            a = array.array(_array_fmts[self._sampwidth])
            a.fromstring(data)
            data = a
            assert data.itemsize == self._sampwidth
            data.byteswap()
            #data.tofile(self._file)
            self._file.write(data)
            self._datawritten = self._datawritten + len(data) * self._sampwidth
        else:
            if self._sampwidth == 3 and sys.byteorder == 'big':
                data = _byteswap3(data)
            self._file.write(data)
            self._datawritten = self._datawritten + len(data)
        self._nframeswritten = self._nframeswritten + nframes

    def writeframes(self, data):
        self.writeframesraw(data)
        if self._datalength != self._datawritten:
            self._patchheader()
        return self._file

    def close(self):
        if self._file:
            try:
                self._ensure_header_written(0)
                if self._datalength != self._datawritten:
                    self._patchheader()
                self._file.flush()
            finally:
                self._file = None
        if self._i_opened_the_file:
            self._i_opened_the_file.close()
            self._i_opened_the_file = None

    #
    # Internal methods.
    #

    def _ensure_header_written(self, datasize):
        if not self._headerwritten:
            if not self._nchannels:
                raise Error, '# channels not specified'
            if not self._sampwidth:
                raise Error, 'sample width not specified'
            if not self._framerate:
                raise Error, 'sampling rate not specified'
            self._write_header(datasize)

    def _write_header(self, initlength):
        assert not self._headerwritten
        self._file.write('RIFF')
        if not self._nframes:
            self._nframes = initlength / (self._nchannels * self._sampwidth)
        self._datalength = self._nframes * self._nchannels * self._sampwidth
        self._form_length_pos = self._file.tell()
        self._file.write(struct.pack('<L4s4sLHHLLHH4s',
            36 + self._datalength, 'WAVE', 'fmt ', 16,
            WAVE_FORMAT_PCM, self._nchannels, self._framerate,
            self._nchannels * self._framerate * self._sampwidth,
            self._nchannels * self._sampwidth,
            self._sampwidth * 8, 'data'))
        self._data_length_pos = self._file.tell()
        self._file.write(struct.pack('<L', self._datalength))
        self._headerwritten = True

    def _patchheader(self):
        assert self._headerwritten
        if self._datawritten == self._datalength:
            return
        curpos = self._file.tell()
        self._file.seek(self._form_length_pos, 0)
        self._file.write(struct.pack('<L', 36 + self._datawritten))
        self._file.seek(self._data_length_pos, 0)
        self._file.write(struct.pack('<L', self._datawritten))
        self._file.seek(curpos, 0)
        self._datalength = self._datawritten

def open(path,flag):
    return Wave_write()