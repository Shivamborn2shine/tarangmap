package com.tarang.collector

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.net.wifi.WifiManager
import android.os.Build
import android.telephony.CellInfoLte
import android.telephony.CellInfoNr
import android.telephony.CellSignalStrengthNr
import android.telephony.TelephonyManager
import androidx.core.content.ContextCompat

data class RadioSnapshot(
    val wifiAvailable: Boolean,
    val wifiRssiDbm: Int?,
    val wifiFrequencyMhz: Int?,
    val wifiSsid: String?,
    val wifiMissingReason: String?,
    val cellTech: String?,
    val lteRsrpDbm: Int?,
    val lteRsrqDb: Int?,
    val nrSsRsrpDbm: Int?,
    val nrSsRsrqDb: Int?,
    val nrSsSinrDb: Int?,
    val cellMissingReason: String?,
)

/**
 * Permission-aware Android Wi-Fi & Telephony probe.
 * Never fabricates missing values or hides OS scan throttling.
 */
class RadioCapabilityProbe(private val context: Context) {

    fun capture(): RadioSnapshot {
        val hasFineLocation = ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED

        val wifiManager = context.applicationContext.getSystemService(Context.WIFI_SERVICE) as? WifiManager
        var wifiRssi: Int? = null
        var wifiFreq: Int? = null
        var wifiSsid: String? = null
        var wifiReason: String? = null

        if (wifiManager == null) {
            wifiReason = "WifiManager unavailable on this device"
        } else if (!hasFineLocation) {
            wifiReason = "ACCESS_FINE_LOCATION not granted"
        } else {
            @Suppress("DEPRECATION")
            val info = wifiManager.connectionInfo
            if (info != null && info.rssi != -127) {
                wifiRssi = info.rssi
                wifiFreq = info.frequency
                wifiSsid = info.ssid?.removePrefix("\"")?.removeSuffix("\"")
            } else {
                wifiReason = "Wi-Fi not connected or RSSI unavailable"
            }
        }

        val telephony = context.getSystemService(Context.TELEPHONY_SERVICE) as? TelephonyManager
        var cellTech: String? = null
        var lteRsrp: Int? = null
        var lteRsrq: Int? = null
        var nrRsrp: Int? = null
        var nrRsrq: Int? = null
        var nrSinr: Int? = null
        var cellReason: String? = null

        if (telephony == null) {
            cellReason = "TelephonyManager unavailable"
        } else if (!hasFineLocation) {
            cellReason = "ACCESS_FINE_LOCATION required for CellInfo"
        } else {
            val cells = telephony.allCellInfo.orEmpty().filter { it.isRegistered }
            if (cells.isEmpty()) {
                cellReason = "No registered cell info returned by modem"
            } else {
                for (cell in cells) {
                    if (cell is CellInfoLte) {
                        cellTech = "LTE"
                        val s = cell.cellSignalStrength
                        lteRsrp = s.rsrp.takeIf { it != Int.MAX_VALUE }
                        lteRsrq = s.rsrq.takeIf { it != Int.MAX_VALUE }
                    } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q && cell is CellInfoNr) {
                        cellTech = "NR"
                        val s = cell.cellSignalStrength as? CellSignalStrengthNr
                        if (s != null) {
                            nrRsrp = s.ssRsrp.takeIf { it != Int.MAX_VALUE }
                            nrRsrq = s.ssRsrq.takeIf { it != Int.MAX_VALUE }
                            nrSinr = s.ssSinr.takeIf { it != Int.MAX_VALUE }
                        }
                    }
                }
            }
        }

        return RadioSnapshot(
            wifiAvailable = wifiRssi != null,
            wifiRssiDbm = wifiRssi,
            wifiFrequencyMhz = wifiFreq,
            wifiSsid = wifiSsid,
            wifiMissingReason = wifiReason,
            cellTech = cellTech,
            lteRsrpDbm = lteRsrp,
            lteRsrqDb = lteRsrq,
            nrSsRsrpDbm = nrRsrp,
            nrSsRsrqDb = nrRsrq,
            nrSsSinrDb = nrSinr,
            cellMissingReason = cellReason,
        )
    }
}
