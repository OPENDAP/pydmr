
class TestResults:
    misc_results = []
    misc_total = 0
    error_count = 0
    info_count = 0

    dmr_results = []
    dmr_total = 0
    dmr_pass = 0
    dmr_fail = 0

    dap_results = []
    dap_total = 0
    dap_pass = 0
    dap_fail = 0

    dap_var_results = []
    dap_var_total = 0
    dap_var_pass = 0
    dap_var_fail = 0

    netcdf_results = []
    netcdf_total = 0
    netcdf_pass = 0
    netcdf_fail = 0

    def __init__(self):
        self.misc_results = []

    def add_misc(self, result):
        self.misc_results.append(result)
        self.misc_total += 1
        if result.status == "error":
            self.error_count += 1
        if result.status == "info":
            self.info_count += 1

    def add_dmr(self, result):
        self.dmr_results.append(result)
        self.dmr_total += 1
        if result.status == "pass":
            self.dmr_pass += 1
        if result.status == "fail":
            self.dmr_fail += 1

    def add_dap(self, result):
        self.dap_results.append(result)
        self.dap_total += 1
        if result.status == "pass":
            self.dap_pass += 1
        if result.status == "fail":
            self.dap_fail += 1

    def add_dap_var(self, result):
        self.dap_var_results.append(result)
        self.dap_var_total += 1
        if result.status == "pass":
            self.dap_var_pass += 1
        if result.status == "fail":
            self.dap_var_fail += 1

    def add_netcdf(self, result):
        self.netcdf_results.append(result)
        self.netcdf_total += 1
        if result.status == "pass":
            self.netcdf_pass += 1
        if result.status == "fail":
            self.netcdf_fail += 1


class Result:
    #  provider level
    provider = ""
    ccid = ""
    title = ""

    #  collection level
    gid = ""
    url = ""

    #  test level
    type = ""  # dmr, dap, dap_var
    status = ""  # pass, fail, error, info
    code = ""  # 200, 404, 403
    payload = ""

    def __init__(self, typ, status, code):
        self.type = typ
        self.status = status
        self.code = code

    def addprovider(self, pro, ccid, title):
        self.provider = pro
        self.ccid = ccid
        self.title = title
