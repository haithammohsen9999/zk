from __future__ import unicode_literals


def get_data(data=''):
	return {
		'fieldname': 'device',
		# 'non_standard_fieldnames': {
		# 	'Employee Checkin': 'device_id',
		# },
		'transactions': [
			{
				'label': 'Logs',
				'items': ['Device Log']
			},
			{
				'label': 'Employee Checkin',
				'items': ['Employee Checkin']
			}
		]
	}
