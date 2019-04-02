#include "GIMMEToolUI.h"
#include <QtWidgets/QApplication>

int main(int argc, char *argv[])
{
	QApplication a(argc, argv);
	GIMMEToolUI w;
	w.show();
	return a.exec();
}
