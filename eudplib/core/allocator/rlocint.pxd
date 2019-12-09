# cython: language_level=3

cdef class RlocInt_C:
    cdef public size_t offset, rlocmode

cpdef RlocInt_C RlocInt(offset, rlocmode)
cpdef RlocInt_C toRlocInt(x)
