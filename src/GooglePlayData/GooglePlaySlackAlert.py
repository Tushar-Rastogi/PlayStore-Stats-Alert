import os
import shutil
import datetime
import pandas as pd
from slack_sdk.webhook import WebhookClient
import json
import PlotData as pD


class GooglePlayAlert:
    data_points = {
        'Start date': (1, 2),
        'End date': (1, 3),
        'Daily User Uninstalls': (4, 2),
        'Uninstall events': (4, 3),
        'Daily User Installs': (7, 2),
        'Install events': (7, 3),
        'Daily Device Installs': (7, 6),
        'Active Device Installs': (7, 7),
        'Update events': (10, 2)
    }
    alert_on_change = 'Uninstall events'
    threshold = 5
    compare_time_days = 8

    def __init__(self, metric_type, grasp, root_path, month):
        self.metric_type = metric_type
        self.grasp = grasp
        self.root_path = root_path
        self.sheet_path = self.root_path + 'Data/PlayStore_Files'
        self.data_map = dict()
        self.month = month
        self.required_data = None

    def check_to_alert(self, dataset, percentage_change, threshold=5):
        if dataset[percentage_change] > threshold:
            print(dataset[percentage_change])
            return True
        else:
            print(dataset[percentage_change])
            return False

    def update_message(self, data, item, value):
        blocks, fields = GooglePlayAlert.data_points[item]
        data['blocks'][blocks]['fields'][fields]['text'] = str(value)

    def slack_push(self, data_map):
        url = 'https://hooks.slack.com/services/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'
        webhook = WebhookClient(url)
        with open(self.root_path + 'src/resources/message.json', mode='r') as json_message:
            data = json.load(json_message)
        for item in data_map.keys():
            self.update_message(data, item, data_map[item])

        with open(self.root_path + '/src/resources/message.json', mode='w') as json_message:
            json.dump(data, json_message)

        if self.check_to_alert(data_map, GooglePlayAlert.alert_on_change, GooglePlayAlert.threshold):
            print('Initiating message for slack Alert!!!')
            response = webhook.send(
                text="fallback",
                blocks=data['blocks']
            )
            assert response.status_code == 200
            assert response.body.title() == "Ok"

    def download_data_sheet(self):
        os.system(
            "gsutil cp -r \"gs://pubsite_prod_rev_06299290395236023813/stats/" + self.metric_type + "/" +
            self.metric_type + "_net.one97.paytm_2021" + month + "_" + self.grasp + ".csv\" " + self.sheet_path
        )
        # return self.metric_type + "_net.one97.paytm_2021" + month + "_" + self.grasp + ".csv"
        return os.listdir(self.sheet_path)

    def clean_directory(self):
        print(f'Cleaning directory "{self.sheet_path}"')
        for filename in os.listdir(self.sheet_path):
            file_path = os.path.join(self.sheet_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def get_percentage_change(self, required_data, data_type):
        previous_date_data = required_data[data_type].iloc[0]
        last_date_data = required_data[data_type].iloc[-1]
        percentage_change_device_install = round(((last_date_data - previous_date_data) / previous_date_data) * 100,
                                                 2)
        self.data_map[data_type] = percentage_change_device_install

    def get_push_data(self, csv_file):
        data = pd.read_csv(self.sheet_path + '/' + csv_file, encoding='utf-16')
        GooglePlayAlert.compare_time_days += 1
        print(GooglePlayAlert.compare_time_days)
        self.required_data = data[
            ['Daily Device Installs', 'Daily User Installs', 'Active Device Installs', 'Update events',
             'Install events',
             'Date', 'Daily User Uninstalls', 'Uninstall events']].tail(GooglePlayAlert.compare_time_days)

        print(self.required_data)
        # quit()
        self.data_map['Start date'] = self.required_data['Date'].iloc[0]
        self.data_map['End date'] = self.required_data['Date'].iloc[-1]
        for data_type in self.required_data:
            if data_type != 'Date':
                self.get_percentage_change(self.required_data, data_type)
        print(self.data_map)
        return self.required_data
        # gpa.slack_push(self.data_map)


if __name__ == '__main__':
    d = datetime.datetime.now()
    global month
    month = d.strftime("%m")
    root, source_dir, file_dir = os.path.abspath(__file__).partition('src')
    gpa = GooglePlayAlert('installs', 'overview', root, month)
    gpa.clean_directory()
    file_name_list = gpa.download_data_sheet()
    if len(file_name_list) == 1:
        file_name = file_name_list[0]
    else:
        raise FileNotFoundError('Mutliple Files found on folder : {}'.format(gpa.sheet_path))
    rd = gpa.get_push_data(file_name)
    pd = pD.PlotData(rd, root, month)
    pd.plot_data(['Uninstall events', 'Install events', 'Update events'])
