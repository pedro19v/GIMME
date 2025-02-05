//#include <pybind11/pybind11.h>
#include <Python.h>
#include <Windows.h>
#include <cmath>
#include "ODPIP.h"
#include "CLink.h"



struct SolverArguments
{
	int numPlayers;
	double* f;
	int minNumberOfPlayersPerGroup;
	int maxNumberOfPlayersPerGroup;
};

PyObject* odpip(PyObject* /*unused module reference*/, PyObject* args) {

	int numPlayers;
	PyObject* arrayOfF;
	int minNumberOfPlayersPerGroup;
	int maxNumberOfPlayersPerGroup;

	if (!PyArg_ParseTuple(args, "iiiO", &numPlayers, &minNumberOfPlayersPerGroup, &maxNumberOfPlayersPerGroup, &arrayOfF))
		return NULL;

	//if (!PyArg_ParseTuple(args, "iii", &numPlayers, &minNumberOfPlayersPerGroup, &maxNumberOfPlayersPerGroup))
		//return NULL;

	PyObject** elems = PySequence_Fast_ITEMS(arrayOfF);
	size_t len = PySequence_Fast_GET_SIZE(arrayOfF);

	double* coalitionValues = (double*)malloc(len * sizeof(double));

	for (size_t i = 0; i < len; i++) {
		coalitionValues[i] = PyFloat_AsDouble(elems[i]);
	}

	ODPIP* odpip = new ODPIP(numPlayers, coalitionValues, minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup);
	odpip->IP();

	std::vector<long> bestCSFound = odpip->bestCSInBitFormat;
	
	free(coalitionValues);
	PyObject* returnArray = PyList_New(bestCSFound.size());
	for (int i = 0; i < bestCSFound.size(); i++)
		PyList_SetItem(returnArray, i, PyLong_FromLong(bestCSFound[i]));

	return returnArray;
}

PyObject* clink(PyObject* /*unused module reference*/, PyObject* args) {

	int numPlayers;
	PyObject* arrayOfF;
	int minNumberOfPlayersPerGroup;
	int maxNumberOfPlayersPerGroup;

	if (!PyArg_ParseTuple(args, "iiiO", &numPlayers, &minNumberOfPlayersPerGroup, &maxNumberOfPlayersPerGroup, &arrayOfF))
		return NULL;

	//if (!PyArg_ParseTuple(args, "iii", &numPlayers, &minNumberOfPlayersPerGroup, &maxNumberOfPlayersPerGroup))
		//return NULL;

	PyObject** elems = PySequence_Fast_ITEMS(arrayOfF);
	size_t len = PySequence_Fast_GET_SIZE(arrayOfF);

	double* coalitionValues = (double*)malloc(len * sizeof(double));

	for (size_t i = 0; i < len; i++) {
		coalitionValues[i] = PyFloat_AsDouble(elems[i]);
	}

	CLink* cLink = new CLink(numPlayers, coalitionValues, minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup);
	cLink->CLinkAlgorithm();

	std::vector<long> bestCSFound = cLink->optimalCSInBitFormat;

	free(coalitionValues);
	PyObject* returnArray = PyList_New(bestCSFound.size());
	for (int i = 0; i < bestCSFound.size(); i++)
		PyList_SetItem(returnArray, i, PyLong_FromLong(bestCSFound[i]));

	return returnArray;
}

/* CPython*/

static PyMethodDef GIMMESolver_methods[]{
	// The first property is the name exposed to Python, fast_tanh
	// The second is the C++ function with the implementation
	// METH_O means it takes a single PyObject argument
	{"odpip", (PyCFunction)odpip, METH_VARARGS, nullptr},
	{"clink", (PyCFunction)clink, METH_VARARGS, nullptr},

	{nullptr, nullptr, 0, nullptr}
};

static PyModuleDef GIMMESolver_module = {
	PyModuleDef_HEAD_INIT,
	"GIMMESolver",								// Module name to use with Python import statements
	"Provides solver functions",				// Module description
	0,
	GIMMESolver_methods								// Structure that defines the methods of the module
};

PyMODINIT_FUNC PyInit_GIMMESolver() {
	return PyModule_Create(&GIMMESolver_module);
}
