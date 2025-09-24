%module hmm
%{
#include "hmm.h"
%}

/* Enable std::vector<int> support */
%include <std_vector.i>
%template(IntVector) std::vector<int>;

%include "hmm.h"