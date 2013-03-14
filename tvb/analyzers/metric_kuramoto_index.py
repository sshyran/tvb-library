# -*- coding: utf-8 -*-
#
#
# (c)  Baycrest Centre for Geriatric Care ("Baycrest"), 2012, all rights reserved.
#
# No redistribution, clinical use or commercial re-sale is permitted.
# Usage-license is only granted for personal or academic usage.
# You may change sources for your private or academic use.
# If you want to contribute to the project, you need to sign a contributor's license. 
# Please contact info@thevirtualbrain.org for further details.
# Neither the name of Baycrest nor the names of any TVB contributors may be used to endorse or 
# promote products or services derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY BAYCREST ''AS IS'' AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, 
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL BAYCREST BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS 
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
#
#

"""
Filler analyzer: Takes a TimeSeries object and returns a Float.

.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""
# standard library
import cmath
import numpy
import tvb.analyzers.metrics_base as metrics_base
import tvb.datatypes.time_series as time_series_module
from tvb.basic.filters.chain import FilterChain
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)



class KuramotoIndex(metrics_base.BaseTimeseriesMetricAlgorithm):
    """
    Return the Kuramoto synchronization index. 
    
    Useful metric for a parameter analysis when the collective brain dynamics
    represent coupled oscillatory processes.
    
    The *order* parameters are :math:`r` and :math:`Psi`.
    
    .. math::
        r \\exp(i * \\psi) &= \\frac{1}{N}\\,\\sum(\\exp(i*\\theta)
    
    The first is the phase coherence of the population of oscillators (KSI) 
    and the second is the average phase.
    
    When :math:`r=0` means 0 coherence among oscillators.
    
    
    Input:
    TimeSeries datatype 
    
    Output: 
    Float
    
    This is a crude indicator of synchronization among nodes over the entire 
    network.

    #NOTE: For the time being it is meant to be another global metric.
    However, it should be consider to have a sort of TimeSeriesDatatype for this
    analyzer.
    
    """
    
    time_series = time_series_module.TimeSeries(
        label = "Time Series", 
        required = True,
        doc="""The TimeSeries for which the Kuramoto Synchronization Index
        will be computed""")
        
    
    accept_filter = FilterChain(operations = ["==", ">="], values = [4, 2],
                                fields=[FilterChain.datatype + '._nr_dimensions', FilterChain.datatype + '._length_2d'])
    
    
    def evaluate(self):
        """
        Kuramoto Synchronization Index
        """
        cls_attr_name = self.__class__.__name__+".time_series"
        self.time_series.trait["data"].log_debug(owner = cls_attr_name)
        
        
        if self.time_series.data.shape[1]  < 2:
            msg = " The number of state variables should be at least 2."
            LOG.error(msg)
            raise Exception, msg
                
        #TODO: Should be computed for each possible combination of var, mode
        #      for var, mode in itertools.product(range(self.time_series.data.shape[1]), 
        #                                         range(self.time_series.data.shape[3])):
        
        #TODO: Generalise. The Kuramoto order parameter is computed over sliding 
        #      time windows and then normalised    
        
        theta_sum = numpy.sum(numpy.exp(0.0 + 1j * (numpy.vectorize(cmath.polar)
                    (numpy.vectorize(complex)(self.time_series.data[:, 0, :, 0], 
                     self.time_series.data[:, 1, :, 0]))[1])), axis=1)
                     
        result = numpy.vectorize(cmath.polar)(theta_sum / self.time_series.data.shape[2])

        return result[0].mean()   
    
    
    def result_shape(self):
        """
        Returns the shape of the main result of the ... 
        """
        return (1,)
    
    
    def result_size(self):
        """
        Returns the storage size in Bytes of the results of the ... .
        """
        return 8.0 #Bytes
    
    
    def extended_result_size(self):
        """
        Returns the storage size in Bytes of the extended result of the ....
        That is, it includes storage of the evaluated ...
        """
        return 8.0 #Bytes

