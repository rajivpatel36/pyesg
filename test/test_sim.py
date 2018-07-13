from pyesg.configuration.pyesg_configuration import *
config = PyESGConfiguration()
config.number_of_projection_steps = 30
config.number_of_batches = 1
config.number_of_simulations = 100
config.projection_frequency = 'annually'
config.random_seed = 128
config.start_date = '2018-01-01'
economy = Economy()
economy.id = "GBP"
asset_class = AssetClass()
asset_class.id = "GBP_Nominal"
asset_class.model_id = 'hull_white'
asset_class.add_parameter('alpha', 0.05)
asset_class.add_parameter('sigma', 0.02)

yc_points = {
    0.5: 0.00679070105770901,
    1: 0.00745916002218801,
    1.5: 0.0079074852733388,
    2: 0.00836441669643775,
    2.5: 0.00884161282573678,
    3: 0.00932762601832977,
    3.5: 0.00981445589941161,
    4: 0.0102969721178294,
    4.5: 0.0107716710398867,
    5: 0.0112363849191675,
    5.5: 0.0116900851233338,
    6: 0.0121325124408309,
    6.5: 0.0125637162796559,
    7: 0.0129837371605093,
    7.5: 0.0133924143022063,
    8: 0.0137892855650153,
    8.5: 0.0141736214537358,
    9: 0.0145445182679629,
    9.5: 0.0149010412164557,
    10: 0.0152422849420296,
    10.5: 0.0155674503497323,
    11: 0.0158758864638649,
    11.5: 0.0161671188651251,
    12: 0.0164409074632115,
    12.5: 0.016697217851849,
    13: 0.0169361824548138,
    13.5: 0.0171580886888855,
    14: 0.0173633870307634,
    14.5: 0.0175526692648801,
    15: 0.0177266234016501,
    15.5: 0.0178859783210095,
    16: 0.0180314895849257,
    16.5: 0.0181639353683754,
    17: 0.018284106311916,
    17.5: 0.0183927617968095,
    18: 0.018490607925128,
    18.5: 0.0185782967490554,
    19: 0.0186563922209754,
    19.5: 0.0187253557221218,
    20: 0.018785557677642,
    20.5: 0.0188372886488034,
    21: 0.0188807683798148,
    21.5: 0.0189161404104334,
    22: 0.0189434581524923,
    22.5: 0.0189627104915117,
    23: 0.0189738426838589,
    23.5: 0.0189767792253448,
    24: 0.0189714599105421,
    24.5: 0.018957845218761,
    25: 0.0189359147882514,
    25.5: 0.0189056816921497,
    26: 0.0188672208215708,
    26.5: 0.0188206722776286,
    27: 0.0187662444763932,
    27.5: 0.0187042132382632,
    28: 0.0186349225161717,
    28.5: 0.0185587809820652,
    29: 0.0184762565449625,
    29.5: 0.0183878727980299,
    30: 0.0182942021898953,
    30.5: 0.0181958450182937,
    31: 0.0180934206282059,
    31.5: 0.0179875657839365,
    32: 0.0178789330057234,
    32.5: 0.0177681797287789,
    33: 0.017655948801948,
    33.5: 0.0175428655247506,
    34: 0.0174295389236686,
    34.5: 0.0173165628801392,
    35: 0.0172045112957245,
    35.5: 0.0170939187050309,
    36: 0.0169852750575237,
    36.5: 0.0168790286221742,
    37: 0.0167755888037096,
    37.5: 0.0166753287335625,
    38: 0.0165785875430073,
    38.5: 0.0164856688754966,
    39: 0.0163968357127189,
    39.5: 0.0163123113348747,
    40: 0.0162322805072689,
}

for key, value in yc_points.items():
    asset_class.add_parameter(f"yc_{key}", value)
asset_class.add_output('GBP_Nominal_Discount_Factor', 'discount_factor')
asset_class.add_output('GBP_Nominal_ZCB_5', 'zero_coupon_bond', term=5)
asset_class.add_output('GBP_Nominal_ZCB_10', 'zero_coupon_bond', term=10)
asset_class.add_output('GBP_Nominal_Bond_Index_10', 'bond_index', term=5)
asset_class.add_output('GBP_Nominal_Cash_Account', 'cash_account')

asset_class.random_drivers.append("GBP_Nominal")

# equity_asset_class = AssetClass()
# equity_asset_class.id = "GBP_Equities"
# equity_asset_class.model_id = 'black_scholes'
# equity_asset_class.add_parameter('sigma', 0.2)
# equity_asset_class.add_output('GBP_Equities_TRI', 'total_return_index', 1)
# equity_asset_class.random_drivers.append("GBP_Equities")
# equity_asset_class.dependencies.append("GBP_Nominal")

economy.asset_classes.append(asset_class)
# economy.asset_classes.append(equity_asset_class)

config.economies.append(economy)
config.output_file_directory = '/Users/rajivpatel/Development/pyesg/tests/test_files/simulation_tests/hull_white_annual_all_outputs'
config.output_file_name = 'comparison'

from pyesg.simulation.run import *
generate_simulations(config)

