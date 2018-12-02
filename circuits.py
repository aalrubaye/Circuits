import itertools
import networkx as nx

__author__ = 'Abdul Rubaye'

g = nx.Graph()

input_compute_files = ['compute1.cir','compute2.cir','compute3.cir','compute4.cir','compute5.cir']
output_compute_files = ['output_compute1.bool', 'output_compute2.bool', 'output_compute3.bool', 'output_compute4.bool', 'output_compute5.bool']

input_test_files = ['test1.bool','test2.bool','test3.bool','test4.bool','test5.bool','EXTRA1.bool', 'EXTRA2.bool']
output_test_files = ['output_test1.cir', 'output_test2.cir', 'output_test3.cir', 'output_test4.cir', 'output_test5.cir', 'output_EXTRA1.cir', 'output_EXTRA2.cir']


# Converts the input files into arrays
def read_from_compute_file(c_ind):
    f_compute = open(input_compute_files [c_ind])
    lines = f_compute.readlines()
    number_of_circuts = int(lines[0])

    circuts_inputs = []
    input_chars = []
    for i in range(0, number_of_circuts):
        circuts_inputs.append(lines[i+1].rsplit())

        # check to see id the var has negation
        # if the var comes after ! then add a True value to the array to recognize it as a negation
        # else False will be added
        if len(circuts_inputs[i][0]) == 1:
            circuts_inputs[i].append(False)
            if circuts_inputs[i][0] not in input_chars:
                input_chars.append(circuts_inputs[i][0])
        else:
            circuts_inputs[i].append(True)
            circuts_inputs[i][0] = (circuts_inputs[i][0])[1]
            if circuts_inputs[i][0] not in input_chars:
                input_chars.append(circuts_inputs[i][0])

    for i in range(0, number_of_circuts):
        result = find_input_and_output(circuts_inputs[i][1], circuts_inputs[i][2])
        circuts_inputs[i][1] = result[0]
        circuts_inputs[i][2] = result[1]

    for i in range(0, number_of_circuts):
        var = circuts_inputs[i][0]
        index = input_chars.index(var)
        circuts_inputs[i].append(index)

    create_truth_table(input_chars, circuts_inputs, c_ind)


def find_input_and_output(var1, var2):
    flip = False
    if var1 == '0':
        input = var1
        output = var2
    elif var2 == '0':
        input = var2
        output = var1
    elif var1 == '1':
        output = var1
        input = var2
    elif var2 == '1':
        output = var2
        input = var1
    else:
        input = var1
        output = var2
        flip = True

    return input, output, flip

# prepares the truth table and send each inputs to other functions find the output
def create_truth_table(input_chars, circuits_inputs, c_ind):

    number_of_inputs = len(input_chars)
    table = list(itertools.product([0, 1], repeat=number_of_inputs))

    find_total_res(circuits_inputs, input_chars, table, c_ind)


# a function to find the low or high voltage based on the given input variable
def find_res_val(tt, negate):
    if negate:
        if tt == 1:
            return 0
        else:
            return 1
    else:
        return tt


# performing arithmetic or between two values
def arithmetic_or(v1, v2):
    if v1 == 1 and v2 == 1:
        return 1
    else:
        return v1+v2


# generates a graph and calculates the path's values
# each value is essentially like performing arithmetic or between all the edges of this path
def find_total_res(circuits_inputs, input_chars, table, c_ind):

    f_output = open(output_compute_files[c_ind], 'w')
    number_of_inputs = len(input_chars)
    row = ''
    for i in range (0, number_of_inputs):
        row += input_chars[i][0]+'\t'

    f_output.write(row+'\n')

    for t in table:
        for i in range(0, len(circuits_inputs)):
            node1 = circuits_inputs[i][1]
            node2 = circuits_inputs[i][2]
            negate = circuits_inputs[i][3]
            input_char= circuits_inputs[i][0]
            val = input_chars.index(input_char)
            res_val = find_res_val(t[val], negate)

            if not g.has_edge(node1, node2):
                g.add_edge(node1, node2, value= res_val)
                if g.has_edge('0',node1):
                    if not g.has_edge('0', node2):
                        val1 = g['0'][node1]['value']
                        val2 = g[node1][node2]['value']
                        r = arithmetic_or(val1, val2)
                        g.add_edge('0', node2, value= r)
            else:
                negate=circuits_inputs[i][3]
                input_char= circuits_inputs[i][0]
                val = input_chars.index(input_char)
                res_val = find_res_val(t[val], negate)
                old_val = g[node1][node2]['value']
                new_val = res_val * old_val
                g[node1][node2]['value'] = new_val

        paths = list(nx.all_shortest_paths(g, source='0', target='1'))
        paths_val = []
        for p in paths:
            s = 0
            for i in range (0, len(p)-1):
                node1 = p[i]
                node2 = p[i+1]
                val = g[node1][node2]['value']
                s = arithmetic_or(s, val)
            paths_val.append(s)

        row = ''
        for k in t:
            row += str(k)+'\t'

        if paths_val[0] == 0:
            f_output.write(row+'0\n')
        else:
            f_output.write(row+'1\n')
        g.clear()

    print 'The file ('+ str(input_compute_files[c_ind])+') is completed'


def read_from_test_file(t_ind):
    test_file = open(input_test_files[t_ind])
    output_test_file = open(output_test_files[t_ind], 'w')
    lines = test_file.readlines()
    input_chars = lines[0].rsplit()

    bools_inputs = []
    for i in range(0,(len(input_chars)**2)):
        line = lines[i+1].rsplit()
        if line[2] == '1':
            bools_inputs.append(lines[i+1].rsplit())

    length = len(bools_inputs)
    eq = ''
    rows_to_circuits = []
    for i in range(0,length):
        s = '('
        e = []
        for j in range (0, len(input_chars)):
            if bools_inputs[i][j] == '0':
                v = '!'+input_chars[j]
                s+= v
                e.append(v)
            else:
                v = input_chars[j]
                s += v
                e.append(v)

            if j<len(input_chars)-1:
                s+='.'
        s+=')'
        rows_to_circuits.append(e)
        if i<length-1:
            eq += s+'+'
        else:
            eq += s

    output_test_file.write(str(len(input_chars)**2)+'\n')
    point = 2
    for i in range(0, len(rows_to_circuits)):
        (ep1, ep2, p) = find_endpoints(len(rows_to_circuits[i]), i, point, len(rows_to_circuits))
        point = p
        for k in range(0, len(rows_to_circuits[i])):
            s = rows_to_circuits[i][k]+'\t'+str(ep1[k])+'\t'+str(ep2[k])+'\n'
            output_test_file.write(s)

    print 'The file ('+ str(input_test_files[t_ind])+') is completed'


def find_endpoints(length, index, point, last):

    input = []
    output = []
    p = point
    if index == 0:
        for i in range(0, length):
            input.append(0)
            if index == last-1:
                output.append(1)
            else:
                output.append(point)
        point += 1
    elif index == last-1:
        for i in range(0, length):
            input.append(point)
            output.append(1)
        p = point +1
    else:
        for i in range(0, length):
            input.append(point)
            output.append(point+1)
        p = point + 1

    return input, output, p


if __name__ == "__main__":
    for i in range (0, len(input_compute_files)):
        read_from_compute_file(i)

    print ('-'*40)

    for i in range (0, len(input_test_files)):
        read_from_test_file(i)





