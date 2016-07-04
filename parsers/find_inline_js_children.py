from argparse import ArgumentParser

import common_module
import os
import simplejson as json

EXPRESSION_STATEMENT = 'ExpressionStatement'
EXPRESSION = 'expression'
OPERATOR = 'operator'
BODY = 'body'
TYPE = 'type'
PROPERTY = 'property'
SRC = 'src'
NAME = 'name'
CALL_EXPRESSION = 'CallExpression'
ASSIGNMENT_EXPRESSION = 'AssignmentExpression'
CALLEE = 'callee'
LEFT = 'left'
RIGHT = 'right'
VALUE = 'value'
LITERAL = 'Literal'

def main(root_dir, output_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        process_page(page, root_dir, output_dir)

def process_page(page, root_dir, output_dir):
    common_module.create_directory_if_not_exists(output_dir)
    script_files = os.listdir(os.path.join(root_dir, page))
    print page
    page_output_dir = os.path.join(output_dir, page)
    common_module.create_directory_if_not_exists(page_output_dir)
    output_filename = os.path.join(page_output_dir, 'inline_script_children.txt')
    if os.path.exists(output_filename):
        os.remove(output_filename)
    for script in script_files:
        js_ast_filename = os.path.join(root_dir, page, script)
        with open(js_ast_filename, 'rb') as input_file:
            ast = json.load(input_file)
            children = evaluate_body(ast['body'])
            output_to_file(output_filename, children)

def output_to_file(output_filename, children):
    with open(output_filename, 'ab') as output_file:
        for child in children:
            output_file.write(child + '\n')

def evaluate_body(body_list):
    result = set()
    for statement in body_list:
        # print statement
        if BODY in statement and BODY in statement[BODY]:
            another_body = statement[BODY][BODY]
            result |= evaluate_body(another_body)
        elif TYPE in statement and \
            statement[TYPE] == EXPRESSION_STATEMENT:
            expression = statement[EXPRESSION]
            result |= evaluate_expression(expression)
    return result

def evaluate_expression(expression):
    result = set()
    if TYPE in expression and \
        expression[TYPE] == CALL_EXPRESSION:
        if expression[CALLEE][TYPE] == 'FunctionExpression' and \
            BODY in expression[CALLEE] and \
            BODY in expression[CALLEE][BODY]:
            expression_body = expression[CALLEE][BODY][BODY]
            result |= evaluate_body(expression_body)

    if TYPE in expression and \
        expression[TYPE] == ASSIGNMENT_EXPRESSION and \
        OPERATOR in expression and expression[OPERATOR] == '=':
        lhs = expression[LEFT]
        rhs = expression[RIGHT]
        # Find src on the LHS
        if lhs[TYPE] == 'MemberExpression' and \
            PROPERTY in lhs and \
            NAME in lhs[PROPERTY] and \
            lhs[PROPERTY][NAME] == SRC:
            
            # print expression[RIGHT][RIGHT][TYPE]
            # Now, we can evaluate the rhs.
            if rhs[TYPE] == LITERAL:
                result.add(rhs[VALUE])
            elif rhs[TYPE] == 'BinaryExpression':
                if rhs[RIGHT][TYPE] == LITERAL:
                    # print 'here'
                    result.add(rhs[RIGHT][VALUE])
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
