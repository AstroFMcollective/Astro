from AstroDiscord.components.ini import stats

def reset():
    """Resets all runtime tracking statistics back to 0."""
    stats.set('runtime', 'api_time_spent', '0')
    stats.set('runtime', 'client_time_spent', '0')
    stats.set('runtime', 'avg_api_latency', '0')
    stats.set('runtime', 'avg_client_latency', '0')
    stats.set('runtime', 'successful_requests', '0')
    stats.set('runtime', 'failed_requests', '0')
    
    with open('AstroDiscord/stats.ini', 'w') as stats_file:
        stats.write(stats_file)
        
    print('[AstroDiscord] Runtime stats reset')

def successful_request():
    """Increments the successful request counters."""
    stats.set('runtime', 'successful_requests', str(int(stats['runtime']['successful_requests']) + 1))
    stats.set('lifetime', 'total_successful_requests', str(int(stats['lifetime']['total_successful_requests']) + 1))
    
    with open('AstroDiscord/stats.ini', 'w') as stats_file:
        stats.write(stats_file)
        
    print('[AstroDiscord] Successful request counted')

def failed_request():
    """Increments the failed request counters."""
    stats.set('runtime', 'failed_requests', str(int(stats['runtime']['failed_requests']) + 1))
    stats.set('lifetime', 'total_failed_requests', str(int(stats['lifetime']['total_failed_requests']) + 1))
    
    with open('AstroDiscord/stats.ini', 'w') as stats_file:
        stats.write(stats_file)
        
    print('[AstroDiscord] Failed request counted')

def api_latency(global_io_latency: int):
    """Logs API latency and safely calculates the new average."""
    total_time = int(stats['runtime']['api_time_spent']) + global_io_latency
    success_count = int(stats['runtime']['successful_requests'])
    
    # Safely calculate average to prevent ZeroDivisionError
    avg_latency = total_time // success_count if success_count > 0 else 0
    
    stats.set('runtime', 'api_time_spent', str(total_time))
    stats.set('runtime', 'avg_api_latency', str(avg_latency))
    
    with open('AstroDiscord/stats.ini', 'w') as stats_file:
        stats.write(stats_file)
        
    print('[AstroDiscord] API latency logged')

def client_latency(latency: int):
    """Logs client latency and safely calculates the new average."""
    total_time = int(stats['runtime']['client_time_spent']) + latency
    total_requests = int(stats['runtime']['successful_requests']) + int(stats['runtime']['failed_requests'])
    
    # Safely calculate average to prevent ZeroDivisionError
    avg_latency = total_time // total_requests if total_requests > 0 else 0
    
    stats.set('runtime', 'client_time_spent', str(total_time))
    stats.set('runtime', 'avg_client_latency', str(avg_latency))
    
    with open('AstroDiscord/stats.ini', 'w') as stats_file:
        stats.write(stats_file)
        
    print('[AstroDiscord] Client latency logged')