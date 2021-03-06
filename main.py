import math
import matplotlib.pyplot as plt


#  DEBUGGING
# data_path = 'C:\work\inputOutputExamples\workingCols\input.txt'
# data_path = 'c:\work\inputOutputExamples\workingRows\input.txt'
data_path = input("Please insert file path:")


# checks equality of substring number for all lines
def check_rows(splt_lines):
    for i in range(1, len(splt_lines)):
        if len(splt_lines[0]) != len(splt_lines[i]):
            return 'Input file error: Data lists are not the same length.'

    return []


# transpose string matrix
# splt_lines are presumed having same number of substrings
# according for previous validity checks
def transpose(splt_lines):
    for row in splt_lines:
        splt_lines = [[splt_lines[j][i] for j in range(len(splt_lines))] for i in range(len(splt_lines[0]))]
        return splt_lines


# converts string to float
def str2float(s):
    try:
        v = float(s)
    except ValueError:
        return math.nan
    return v


# converts list of strings to list of floats
# invalid strings become nan
def strlist2floatlis(ss):
    ff = []
    for item in ss:
        ff.append(str2float(item))
    return ff


# check data validity for cast to float
def isvalid_data_columns(splt_lines):
    for line in splt_lines[1:]:
        vv = strlist2floatlis(line)
        if len(vv) != 4:
            return 'Input file error: Data lists are not the same length.'
        elif math.nan in vv:
            return 'Input file error: Data contains not-a-numbers.'

    return []


# forms data matrix for linfit
# i.e. cast strings to proper types
def setdata_columns(splt_lines):
    xydxdy = [[], [], [], []]

    x_ind = splt_lines[0].index('x')
    dx_ind = splt_lines[0].index('dx')
    y_ind = splt_lines[0].index('y')
    dy_ind = splt_lines[0].index('dy')

    for line in splt_lines[1:]:
        vv = strlist2floatlis(line)
        xydxdy[0].append(vv[x_ind])
        xydxdy[1].append(vv[y_ind])
        xydxdy[2].append(vv[dx_ind])
        xydxdy[3].append(vv[dy_ind])

    return xydxdy


# checks   uncertainties
def all_uncertainties_positive(vv):
    all_positve = sum(1 for v in vv if v < 0) == 0
    return all_positve


# dot product for two lists
# assuming same length according to
# checking data on input
def dot_list(x, y):
    ret = 0
    for index, x_item in enumerate(x):
        ret += x_item * y[index]
    return ret


# chi^2 computation for ax+b = y wrt. uncertainties dy
def chi_sqr(x, y, a, b, dy):
    v = []
    for index, x_item in enumerate(x):
        v.append((y[index] - a * x_item - b) / dy[index])
    vv = [(v1 * v1) for v1 in v]
    return sum(vv)


# main function
def fitlin(filename):
    try:
        with open(filename) as f:
            lines = f.readlines()
        f.closed
    except:
        print('fails opening input file')
        return

    splt_lines0 = []
    for line in lines:
        splt_lines0.append(line.strip().lower().split())

    #data for chi computation
    data_lines = splt_lines0[0:splt_lines0.index([])]
    #axis lables
    abrv_lines = lines[1+splt_lines0.index([]):]
    if len(data_lines) == 4:  # row style data
        errMsg = check_rows(data_lines)
        if (errMsg != []):
            print(errMsg)
            return
        #transpose of 'strings' matrix - candidates for transforming to actual data
        data_lines = transpose(data_lines)

    #check of validity for variables abbreviation string
    xydxdy_check = set(sorted(data_lines[0])) & set(sorted(['x', 'y', 'dx', 'dy']))
    if len(xydxdy_check) != 4:
        print('data abreviations are different from agreed "x","y","dx","dy" ')
        return

    errMessage = isvalid_data_columns(data_lines)
    if errMessage != []:
        print(errMessage)
        return
    else:
        xydxdy = setdata_columns(data_lines)

    if all_uncertainties_positive(xydxdy[2] + xydxdy[3]) == False:
        print('Input file error: Not all uncertainties are positive.')
        return

    x = xydxdy[0]
    y = xydxdy[1]
    dx = xydxdy[2]
    dy = xydxdy[3]

    #linfit computation
    one_over_dydy = [1.0 / (v * v) for v in dy]
    sum_one_over_dydy = sum(one_over_dydy)
    x_tag = dot_list(x, one_over_dydy) / sum_one_over_dydy
    y_tag = dot_list(y, one_over_dydy) / sum_one_over_dydy

    xy = [a * b for a, b in zip(x, y)]
    xy_tag = dot_list(xy, one_over_dydy) / sum_one_over_dydy
    xx = [a * b for a, b in zip(x, x)]
    xx_tag = dot_list(xx, one_over_dydy) / sum_one_over_dydy

    DEN = (xx_tag - x_tag * x_tag) # denominator
    a = (xy_tag - x_tag * y_tag) / DEN
    b = y_tag - a * x_tag

    dydy = [a * b for a, b in zip(dy, dy)]
    dydy_tag = dot_list(dydy, one_over_dydy) / sum_one_over_dydy

    N = len(x)
    da = math.sqrt(dydy_tag / (N * DEN))
    db = math.sqrt(dydy_tag * xx_tag / (N * DEN))

    chichi = chi_sqr(x, y, a, b, dy)
    chichi_red = chichi / (N - 2)

    print("a = {0:17.15f} +- {1:19.17f}".format(a, da))
    print("b = {0:17.15f} +- {1:19.17f}".format(b, db))
    print("chi2 = {0:17.15f}".format(chichi))
    print("chi2_reduced = {0:17.15f}".format(chichi_red))

    #lable strings interpretation:
    #substring before ':' is key for substring after it
    id_lable = {}
    for line in abrv_lines:
        ss = line.split(':')
        if len(ss)>1:
            id_lable[ss[0].lower()] = ss[1]
        #otherwise such a strin is out of <key>:<value> convention


    xlable = "x axis"
    if id_lable.get(xlable) != None:
       xlable = id_lable[xlable].strip()
    ylable = "y axis"
    if id_lable.get(ylable) != None:
        ylable = id_lable[ylable].strip()

    x_lefts = [x_value - dx[index]  for index, x_value in enumerate(x)]
    x_right = [x_value + dx[index]  for index, x_value in enumerate(x)]
    y_up    = [y_value - dy[index]  for index, y_value in enumerate(y)]
    y_lo    = [y_value + dy[index]  for index, y_value in enumerate(y)]

    plt.plot(x, y, 'r.')
    plt.xlabel(xlable)
    plt.ylabel(ylable)
    # plt.title('Histogram of IQ')
    for ii in range(0,len(x)):
        plt.plot([x_lefts[ii], x_right[ii]], [y[ii]   , y[ii]   ], 'b')
        plt.plot([x[ii]      , x[ii]      ], [y_up[ii], y_lo[ii]], 'b')

    line_xx = [ min(x), max(x)]
    line_yy = [a*v + b for v in line_xx]

    plt.plot(line_xx, line_yy, 'r-')
    plt.show()

fitlin(data_path)
