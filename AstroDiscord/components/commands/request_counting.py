from AstroDiscord.components.ini import stats

def reset():
	stats.set('runtime', 'api_time_spent', str(0))
	with open('AstroDiscord/stats.ini', 'w') as stats_file:
		stats.write(stats_file)
	stats.set('runtime', 'client_time_spent', str(0))
	with open('AstroDiscord/stats.ini', 'w') as stats_file:
		stats.write(stats_file)
	stats.set('runtime', 'avg_api_latency', str(0))
	with open('AstroDiscord/stats.ini', 'w') as stats_file:
		stats.write(stats_file)
	stats.set('runtime', 'avg_client_latency', str(0))
	with open('AstroDiscord/stats.ini', 'w') as stats_file:
		stats.write(stats_file)
	stats.set('runtime', 'successful_requests', str(0))
	with open('AstroDiscord/stats.ini', 'w') as stats_file:
		stats.write(stats_file)
	stats.set('runtime', 'failed_requests', str(0))
	with open('AstroDiscord/stats.ini', 'w') as stats_file:
		stats.write(stats_file)
	print('[AstroDiscord] Runtime stats reset')

def successful_request():
	stats.set('runtime', 'successful_requests', str(int(stats['runtime']['successful_requests']) + 1))
	with open('AstroDiscord/stats.ini', 'w') as stats_file:
		stats.write(stats_file)
	stats.set('lifetime', 'total_successful_requests', str(int(stats['lifetime']['total_successful_requests']) + 1))
	with open('AstroDiscord/stats.ini', 'w') as stats_file:
		stats.write(stats_file)
	print('[AstroDiscord] Successful request counted')

def failed_request():
	stats.set('runtime', 'failed_requests', str(int(stats['runtime']['failed_requests']) + 1))
	with open('AstroDiscord/stats.ini', 'w') as stats_file:
		stats.write(stats_file)
	stats.set('lifetime', 'total_failed_requests', str(int(stats['lifetime']['total_failed_requests']) + 1))
	with open('AstroDiscord/stats.ini', 'w') as stats_file:
		stats.write(stats_file)
	print('[AstroDiscord] Failed request counted')

def api_latency(global_io_latency: int):
	stats.set('runtime', 'api_time_spent', str(int(stats['runtime']['api_time_spent']) + global_io_latency))
	with open('AstroDiscord/stats.ini', 'w') as stats_file:
		stats.write(stats_file)
	stats.set('runtime', 'avg_api_latency', str(int(stats['runtime']['api_time_spent']) // int(stats['runtime']['successful_requests'])))
	with open('AstroDiscord/stats.ini', 'w') as stats_file:
		stats.write(stats_file)
	print('[AstroDiscord] API latency logged')

def client_latency(client_latency: int):
	stats.set('runtime', 'client_time_spent', str(int(stats['runtime']['client_time_spent']) + client_latency))
	with open('AstroDiscord/stats.ini', 'w') as stats_file:
		stats.write(stats_file)
	stats.set('runtime', 'avg_client_latency', str(int(stats['runtime']['client_time_spent']) // (int(stats['runtime']['successful_requests']) + int(stats['runtime']['failed_requests']))))
	with open('AstroDiscord/stats.ini', 'w') as stats_file:
		stats.write(stats_file)
	print('[AstroDiscord] Client latency logged')