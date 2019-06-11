using System.Collections;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using UnityEngine;

class GIMMEBridge
{
    [DllImport("GIMMECore")]
    public static extern void addPlayer(int id, string name, int numPastModelIncreasesCells, int maxAmountOfStoredProfilesPerCell, int numStoredPastIterations);

    [DllImport("GIMMECore")]
    public static extern void getPlayerCharacteristics(int id, byte[] retStr);

    [DllImport("GIMMECore")]
    public static extern void initAdaptation();

    [DllImport("GIMMECore")]
    public static extern void iterate(byte[] retStr);
}
