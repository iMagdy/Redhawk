#!/usr/bin/env python
""" Convert C-Tree to ast. """

import redhawk.common.node as N
import redhawk.common.node_position as NP
import redhawk.common.types as T

# Map C operators into the LAST operators
BINARY_OPERATOR_CONVERSIONS = {
      '+'  : 'ADD'
     ,'-'  : 'MINUS'
     ,'*'  : 'MULTIPLY'
     ,'/'  : 'DIVIDE'
     ,'^'  : 'BITWISE_XOR'
     ,'|'  : 'BITWISE_OR'
     ,'&'  : 'BITWISE_AND'
     ,'<<' : 'LSHIFT'
     ,'>>' : 'RSHIFT'
     ,'%'  : 'MOD'
     ,'<'  : 'LT'
     ,'>'  : 'GT'
     ,'<=' : 'LTE'
     ,'>=' : 'GTE'
     ,'==' : 'EQ'
     ,'!=' : 'NOT_EQ'
     ,'&&' : 'BOOLEAN_AND'
     ,'||' : 'BOOLEAN_OR'
}

UNARY_OPERATOR_CONVERSIONS = {
      '+'  : 'UNARY_PLUS'
     ,'-'  : 'UNARY_MINUS'
}


def GetCoords(t):
  assert(t is not None)
  c = t.coord
  assert(c is not None)
  return NP.NodePosition(c.file, c.line, c.column)

class CTreeConverter:
  def __init__(self, filename=None):
    self.filename = filename
    return

  def ThrowNotImplementedError(self, tree):
    raise NotImplementedError("Convert%s not implemented."%(tree.__class__.__name__.capitalize()))

  def ConvertTree(self, tree):
    method = "Convert" + tree.__class__.__name__.capitalize()
    visitor = getattr(self, method, self.ThrowNotImplementedError)
    return visitor(tree)

  def ConvertFileast(self, tree):
    position = NP.NodePosition(self.filename, 0, 0)
    return N.Module(position,
        children = map(self.ConvertTree, tree.children()))

  def ConvertReturn(self, tree):
    return N.Return(GetCoords(tree), 
        return_expression = self.ConvertTree(tree.expr))

  def ConvertConstant(self, tree):
    return N.Constant(GetCoords(tree), 
        value = tree.value, type = T.BaseType(tree.type))

  def ConvertId(self, tree):
    #TODO(spranesh): Is this assert always true?
    if tree.name == 'NULL':
      return N.Constant(GetCoords(tree), 
          value = tree.name, 
          type = T.Pointer(T.BaseType('NULL')))
    else:
      return N.VariableReference(GetCoords(tree), 
          name = tree.name)

  def ConvertDecl(self, tree):
    t = self.ConvertTree(tree.type)
    if isinstance(t, N.DeclareFunction):
      t.name = tree.name
      t.storage = tree.storage
      t.quals = tree.quals
      return t
    else: 
      return N.DefineVariable(GetCoords(tree), 
        name = tree.name, 
        init = self.ConvertTree(tree.init),
        type = t,
        storage = tree.storage,
        quals = tree.quals)

  def ConvertTypename(self, tree):
    #TODO(spranesh): Handle quals.
    t = self.ConvertTree(tree.type)
    return N.DefineVariable(None, # No coords for Typename
        name = tree.name,
        type = t)

  def ConvertTypedecl(self, tree):
    """ Returns Type Object """
    try:
      return T.BaseType(base_type = tree.type.names[0])
    except IndexError, e:
      # Default type is int in C
      return T.BaseType(base_type = 'int')

  def ConvertPtrdecl(self, tree):
    # TODO(spranesh): Handle quals (such as constants)
    """ Returns Type Object """
    return T.Pointer(ptr_type = self.ConvertTree(tree.type))

  def ConvertArraydecl(self, tree):
    # TODO(spranesh): Handle array dimensions.
    """ Returns Type Object """
    return T.Array(array_type = self.ConvertTree(tree.type))

  def ConvertNonetype(self, tree):
    """ Handle cases when children are none."""
    return None

  def ConvertFuncdecl(self, tree):
    """ Handle Function Declarations."""
    try:
      arguments = map(self.ConvertTree, tree.args.params)
    except AttributeError, e:
      arguments = []

    return N.DeclareFunction(
        position = GetCoords(tree),
        name = None,
        arguments = arguments,
        return_type = self.ConvertTree(tree.type))

  def ConvertFuncdef(self, tree):
    """ Handle Function Declarations. Consists of body, and decl.
        body is a compound statement, and decl is a Declaration."""
    #TODO(spranesh): Handle param_decls, (K&R style of arguments)
    # int main(a)
    # char a;
    func_decl = self.ConvertTree(tree.decl)
    body = self.ConvertTree(tree.body)
    return N.DefineFunction(position = GetCoords(tree),
        name = func_decl.name,
        arguments = func_decl.arguments,
        body = body,
        return_type = func_decl.return_type,
        storage = func_decl.storage,
        quals = func_decl.quals)

  def ConvertCompound(self, tree):
    return N.Compound(position = GetCoords(tree),
        compound_items = map(self.ConvertTree, tree.block_items))

  def ConvertBinaryop(self, tree):
    assert(tree.op in BINARY_OPERATOR_CONVERSIONS)
    return N.Expression(position = GetCoords(tree),
        operator = BINARY_OPERATOR_CONVERSIONS[tree.op],
        children = map(self.ConvertTree, [tree.left, tree.right]))
    