
def get_report(file_hash):
    '''
    :param file_hash: md5/sha1/sha256
    :return: json response / None
    '''
    try:
        LOGGER.info("VirusTotal: Check for existing report")
        url = base_url + 'report'
        params = {
            'apikey': apiKey,
            'resource': file_hash
        }
        headers = {"Accept-Encoding": "gzip, deflate"}
        try:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 403:
                LOGGER.error("VirusTotal Permission denied, wrong api key?")
                return None
        except:
            LOGGER.error("VirusTotal ConnectionError, check internet connectivity")
            return None
        try:
            return response.json()
        except ValueError:
            return None
    except Exception as e:
        LOGGER.error(e)
        return None

def get_result(file_path, file_hash):
    '''
    Uoloading a file and getting the approval msg from VT or fetching existing report
    :param file_path: file's path
    :param file_hash: file's hash - md5/sha1/sha256
    :return: VirusTotal result json / None upon error
    '''
    try:
        report = get_report(file_hash)
        if report:
            LOGGER.info("[INFO] Report found.")
            if int(report['response_code']) == 1:
                return report
            elif file_path:
                LOGGER.info("[INFO] VirusTotal: file upload")
                upload_response = upload_file(file_path)
                return upload_response
            else: return "Not found in VirusTotal"
    except Exception as e: LOGGER.info(e)