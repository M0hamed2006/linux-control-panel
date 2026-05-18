import subprocess
import re

class ServiceMonitor:
    """خدمة مراقبة الخدمات (Services)"""
    
    @staticmethod
    def get_all_services():
        """الحصول على قائمة كل الخدمات"""
        try:
            result = subprocess.run(
                ['systemctl', 'list-units', '--type=service', '--all', '--no-pager'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            services = []
            lines = result.stdout.split('\n')[1:]  # تخطي رأس الجدول
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        services.append({
                            'name': parts[0].replace('.service', ''),
                            'status': parts[2],
                            'active': parts[3] if len(parts) > 3 else 'unknown',
                            'description': ' '.join(parts[4:]) if len(parts) > 4 else ''
                        })
            
            return services
        except Exception as e:
            print(f"Service Monitor Error: {e}")
            return []
    
    @staticmethod
    def get_service_status(service_name):
        """الحصول على حالة خدمة معينة"""
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', service_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                'name': service_name,
                'is_active': result.returncode == 0,
                'status': result.stdout.strip()
            }
        except Exception as e:
            return {'name': service_name, 'error': str(e)}
    
    @staticmethod
    def start_service(service_name):
        """تشغيل خدمة"""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'start', service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                'success': result.returncode == 0,
                'message': result.stderr.strip() if result.returncode != 0 else 'Service started'
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def stop_service(service_name):
        """إيقاف خدمة"""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'stop', service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                'success': result.returncode == 0,
                'message': result.stderr.strip() if result.returncode != 0 else 'Service stopped'
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def restart_service(service_name):
        """إعادة تشغيل خدمة"""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'restart', service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                'success': result.returncode == 0,
                'message': result.stderr.strip() if result.returncode != 0 else 'Service restarted'
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def enable_service(service_name):
        """تفعيل خدمة عند الإقلاع"""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'enable', service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                'success': result.returncode == 0,
                'message': result.stderr.strip() if result.returncode != 0 else 'Service enabled'
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def disable_service(service_name):
        """تعطيل خدمة عند الإقلاع"""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'disable', service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                'success': result.returncode == 0,
                'message': result.stderr.strip() if result.returncode != 0 else 'Service disabled'
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
