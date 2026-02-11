
import sys
import os
import unittest

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.strategy_router import get_final_signal

class TestStrategyRouter(unittest.TestCase):
    
    def test_direct_strategy(self):
        """Test standard direct strategy (Thai Market)"""
        # Case: Uptrend Forecast
        res = get_final_signal(forecast_dir=1, probability=70.0, inverse_logic=False)
        self.assertEqual(res['signal_dir'], 1)
        self.assertEqual(res['signal_label'], 'UP')
        self.assertEqual(res['strategy'], 'DIRECT')
        
        # Case: Downtrend Forecast
        res = get_final_signal(forecast_dir=-1, probability=65.0, inverse_logic=False)
        self.assertEqual(res['signal_dir'], -1)
        self.assertEqual(res['signal_label'], 'DOWN')

    def test_inverse_strategy(self):
        """Test inverse strategy (Global Markets)"""
        # Case: Uptrend Forecast -> Should Flip to DOWN
        res = get_final_signal(forecast_dir=1, probability=55.0, inverse_logic=True)
        self.assertEqual(res['signal_dir'], -1)       # FLIPPED
        self.assertEqual(res['signal_label'], 'DOWN') # FLIPPED
        self.assertEqual(res['strategy'], 'INVERSE')
        
        # Case: Downtrend Forecast -> Should Flip to UP
        res = get_final_signal(forecast_dir=-1, probability=52.0, inverse_logic=True)
        self.assertEqual(res['signal_dir'], 1)      # FLIPPED
        self.assertEqual(res['signal_label'], 'UP') # FLIPPED

    def test_neutral_signal(self):
        """Test neutral signals"""
        res = get_final_signal(forecast_dir=0, probability=0, inverse_logic=True)
        self.assertEqual(res['signal_dir'], 0)
        self.assertEqual(res['signal_label'], 'NEUTRAL')

if __name__ == '__main__':
    unittest.main()
