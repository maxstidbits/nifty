#pragma once

#include <boost/pending/disjoint_sets.hpp>
#include <xtensor.hpp>


namespace nifty {
namespace ufd {

    template<class T = uint64_t>
    class BoostUfd {

    public:
        typedef T value_type;

        // initialize from number of elements
        // for consecutive elements
        BoostUfd(const value_type size) : n_elements_(size),
                                          upper_bound_(size),
                                          ranks_(n_elements_),
                                          parents_(n_elements_),
                                          sets_(&ranks_[0], &parents_[0]) {
            for(value_type elem = 0; elem < n_elements_; ++elem) {
                sets_.make_set(elem);
            }
        }


        // initialize from element list for non-consecutive elements
        // NOTE we need to set the ranks and the elements to the number of elements we would
        // have if the elements were continuous (i.e. max + 1)
        template<class ELEMENTS>
        BoostUfd(const xt::xexpression<ELEMENTS> & elements, const std::size_t upper_bound) : n_elements_(elements.derived_cast().size()),
                                                                                         upper_bound_(upper_bound),
                                                                                         ranks_(upper_bound_),
                                                                                         parents_(upper_bound_),
                                                                                         sets_(&ranks_[0], &parents_[0]) {
            const auto & elems = elements.derived_cast();
            for(const value_type elem : elems) {
                sets_.make_set(elem);
            }
        }

        // TODO make const and not const version for path compression ?
        inline value_type find(const value_type elem) {
            return sets_.find_set(elem);
        }


        inline void merge(const value_type elem1, const value_type elem2) {
            // std::cout << "Merge elems " << elem1 << " " << elem2 << std::endl;
            sets_.link(elem1, elem2);
        }


        inline std::size_t numberOfElements() const {
            return n_elements_;
        }

    private:
        std::size_t n_elements_;
        std::size_t upper_bound_;
        std::vector<value_type> ranks_;
        std::vector<value_type> parents_;
        boost::disjoint_sets<value_type*, value_type*> sets_;
    };

}
}
