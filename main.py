import math




#data_path = 'C:/work/fitgui/example-lin.txt'
data_path = 'C:\work\inputOutputExamples\workingCols\input.txt'
#data_path = 'c:\work\inputOutputExamples\workingRows\input.txt'

#check rows
def check_rows(splt_lines):
    for i in range(1, len(splt_lines)):
        if len(splt_lines[0]) != len(splt_lines[i]):
            return 'Input file error: Data lists are not the same length.'

    return []

#transpose
def transpose(splt_lines):
    for row in splt_lines:
        splt_lines = [[splt_lines[j][i] for j in range(len(splt_lines))] for i in range(len(splt_lines[0]))]
        return splt_lines

#converts string to float
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

# check data validity
def isvalid_data_columns(splt_lines):

    for line in splt_lines[1:]:
        vv = strlist2floatlis(line)
        if len(vv)!=4 :
            return 'Input file error: Data lists are not the same length.'
        elif math.nan  in vv:
            return  'Input file error: Data contains not-a-numbers.'

    return []

# forms data matrix for linfit
def setdata_columns(splt_lines):
    xydxdy=[[],[],[],[]]

    x_ind=splt_lines[0].index('x')
    dx_ind = splt_lines[0].index('dx')
    y_ind = splt_lines[0].index('y')
    dy_ind = splt_lines[0].index('dy')

    for line in splt_lines[1:]:
        vv = strlist2floatlis(line)
        xydxdy[0].append(vv[x_ind])
        xydxdy[1].append(vv[y_ind])
        xydxdy[2].append(vv[dx_ind])
        xydxdy[3].append(vv[dy_ind])



    return  xydxdy

#checks   uncertainties
def all_uncertainties_positive(vv):
    all_positve = sum(1 for v in vv if v <0)==0
    return all_positve

#dot product for two lists
#assuming same length according to
#checking data on input
def dot_list(x,y):
    ret= 0
    for index, x_item in enumerate(x):
        ret+= x_item*y[index]
    return ret
#chi
def chi_sqr(x,y,a,b,dy):
    v = []
    for index, x_item in enumerate(x):
        v.append ((y[index] - a*x_item - b)/dy[index])
    vv = [(v1 * v1) for v1 in v]
    return sum(vv)

#main function
def fitlin(filename):
    with open(filename) as f:
        lines = f.readlines()
    f.closed


    splt_lines=[]
    for line in lines:
        splt_lines.append(line.strip().lower().split())

    splt_lines =splt_lines [0:splt_lines.index([])]

    if len(splt_lines) == 4: # row style data
        errMsg = check_rows(splt_lines)
        if(errMsg!=[]):
            print(errMsg)
            return

        splt_lines=transpose(splt_lines)


    xydxdy_check = set(sorted(splt_lines[0])) & set(sorted(['x','y','dx','dy']))
    if len(xydxdy_check) != 4:
        print('data abreviations are different from agreed "x","y","dx","dy" ')
        return

    errMessage = isvalid_data_columns(splt_lines)
    if errMessage !=[]:
        print(errMessage)
        return
    else:
        xydxdy = setdata_columns(splt_lines)



    if all_uncertainties_positive(xydxdy[2]+xydxdy[3])==False :
        print( 'Input file error: Not all uncertainties are positive.')
        return

    x = xydxdy[0]
    y = xydxdy[1]
    dx = xydxdy[2]
    dy = xydxdy[3]

    one_over_dydy = [1.0/(v * v) for v in dy]
    sum_one_over_dydy = sum(one_over_dydy)
    x_tag = dot_list(x,one_over_dydy)/sum_one_over_dydy
    y_tag = dot_list(y,one_over_dydy)/sum_one_over_dydy

    xy = [a*b for a,b in zip(x, y)]
    xy_tag = dot_list(xy,one_over_dydy)/sum_one_over_dydy
    xx = [a * b for a, b in zip(x, x)]
    xx_tag = dot_list(xx,one_over_dydy)/sum_one_over_dydy

    DEN = (xx_tag - x_tag*x_tag)
    a = (xy_tag - x_tag*y_tag)/DEN
    b = y_tag - a*x_tag

    dydy = [a*b for a,b in zip(dy, dy)]
    dydy_tag = dot_list(dydy,one_over_dydy)/sum_one_over_dydy

    N = len(x)
    da = math.sqrt(dydy_tag/(N*DEN))
    db = math.sqrt(dydy_tag*xx_tag/(N*DEN))


    chichi = chi_sqr(x,y,a,b,dy)
    chichi_red = chichi/(N-2)
    bb=9
fitlin(data_path)