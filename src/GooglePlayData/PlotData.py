from matplotlib import pyplot as py
from GooglePlayData import GooglePlaySlackAlert


class PlotData(GooglePlaySlackAlert.GooglePlayAlert):

    # def __init__(self, required_data):
    #     self.__init__()
    #     self.required_Data = required_data
    #     self.date = required_data['Date']
    #     self.uninstall_events = required_data['Uninstall events']
    #     self.install_events = required_data['Install events']
    #     self.update_event = required_data['Update events']

    def __init__(self, required_data, root_path, month):
        self.required_data = required_data
        self.root_path = root_path
        self.month = month

    def plot_data(self, lists):
        # Plot Graph
        print(self.required_data['Date'])
        for x in lists:
            py.plot(self.required_data['Date'], self.required_data[x], label=x)

        py.title('Install/Uninstall/Update Events Overview')
        py.legend()
        py.xlabel('Date')
        py.xticks(rotation=60)
        py.ylabel('Count (million)')
        py.savefig(
            self.root_path + '/Data/Charts/' + 'Ins_Unis_Upd_' + self.month + '.png', bbox_inches="tight", transparent=True
        )
