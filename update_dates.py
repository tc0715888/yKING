import requests
import yaml
import re
from datetime import datetime
import time

def get_expiry_date(domain):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    url = f"https://who.cx/{domain}"
    try:
        response = requests.get(url, headers=headers)
        # 添加更多日期格式的匹配
        patterns = [
            r'Registry Expiry Date: (\d{4}-\d{2}-\d{2})',
            r'Expiry Date: (\d{4}-\d{2}-\d{2})',
            r'Expiration Date: (\d{4}-\d{2}-\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.text)
            if match:
                return match.group(1)
        print(f"Could not find expiry date in response for {domain}")
        return None
    except Exception as e:
        print(f"Error querying {domain}: {str(e)}")
        return None

def update_config():
    try:
        with open('_config.yaml', 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        updated = False
        for domain in config['domains']:
            print(f"Checking {domain['domain']}...")
            expiry_date = get_expiry_date(domain['domain'])
            if expiry_date:
                # 从过期日期倒推一年得到注册/续费日期
                expiry_datetime = datetime.strptime(expiry_date, '%Y-%m-%d')
                registration_date = expiry_datetime.replace(year=expiry_datetime.year - 1)
                new_date = registration_date.strftime('%Y-%m-%d')
                
                if domain['registration_date'] != new_date:
                    domain['registration_date'] = new_date
                    updated = True
                    print(f"Updated {domain['domain']}: {new_date}")
            else:
                print(f"Keeping existing date for {domain['domain']}")
            
            time.sleep(3)  # 增加延时避免请求过快
        
        if updated:
            with open('_config.yaml', 'w', encoding='utf-8') as file:
                yaml.dump(config, file, allow_unicode=True, sort_keys=False)
            print("Config file updated successfully")
        else:
            print("No updates needed")
            
    except Exception as e:
        print(f"Error updating config: {str(e)}")
        raise

if __name__ == "__main__":
    update_config() 
