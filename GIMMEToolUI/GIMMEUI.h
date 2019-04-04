#pragma once

#include <QtWidgets/QMainWindow>
#include "ui_GIMMEToolUI.h"

//include core functionalities
#include "../StudentALSSim/headers/GIMMECore.h"

class GIMMEUI : public QMainWindow
{
	Q_OBJECT

public:
	GIMMEUI(QWidget *parent = Q_NULLPTR);

private:
	Ui::GIMMEToolUIClass ui;
};
