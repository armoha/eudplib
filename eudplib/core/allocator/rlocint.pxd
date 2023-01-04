# cython: language_level=3

cdef class RlocInt_C:
    cdef public size_t offset, rlocmode

cpdef RlocInt_C RlocInt(size_t offset,  size_t rlocmode)
cpdef RlocInt_C toRlocInt(x: _RlocInt)
