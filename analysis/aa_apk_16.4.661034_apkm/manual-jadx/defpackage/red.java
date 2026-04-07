package defpackage;

import android.content.Context;
import android.util.Base64;
import java.math.BigInteger;
import java.nio.ByteBuffer;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.cert.X509Certificate;
import java.util.Arrays;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLEngine;
import javax.net.ssl.SSLEngineResult;
import javax.net.ssl.SSLException;
import javax.net.ssl.SSLPeerUnverifiedException;

/* loaded from: classes.dex */
public final class red {
    public static final xsq a = null;
    public static final byte[] b = null;
    public static final byte[] c = null;
    private static final BigInteger o = null;
    public String d;
    public long e;
    public String f;
    public String g;
    public int h;
    final ree i;
    public final ByteBuffer[] j;
    public SSLContext k;
    public SSLEngine l;
    public int m;
    public int n;
    private final Context p;
    private final Object q;

    static {
        a = nui.n("CAR.GAL.SECURITY");
        o = BigInteger.valueOf(Long.MAX_VALUE);
        b = new byte[]{10, 44, 6, 31, 79, -26, -81, 113, -75, -64, -20, 97, 78, 116, -48, -14, -94, Byte.MIN_VALUE, 35, 7, 119, -105, 80, -1, 44, -84, 48, 70, -63, 108, 112, -112, -25, -9, 6, 124, -10, -109, 11, -17, 25, 52, 85, 52, -82, -101, -124, -31, -82, 7, 48, -39, -53, 15, -32, 35, 55, -14, 34, -92, -6, -106, -64, -41, 1, -91, -17, -41, -102, -111, 63, -65, -100, 8, -13, 117, -36, -8, -60, -53, 94, -42, 99, 47, -80, -75, 75, -49, -8, -70, 107, 32, 56, 40, 63, -121, 25, -16, 82, 57, -97, -4, 55, 17, 69, -100, 54, 39, 15, -17, 81, 123, 30, 5, -17, -80, -52, -79, 6, 118, 88, -80, 5, -113, -9, -78, -18, -1, -38, -51, 10, -36, 20, -63, 42, 71, 39, -2, -2, -41, 63, 110, 35, -107, -41, 66, -93, 105, -96, -77, -59, 34, 108, -77, -45, 85, 25, 54, 54, -112, -66, -93, -48, 46, 3, 32, 126, -15, -95, 119, -19, -66, -124, -99, -101, -87, 18, -41, 95, 51, 92, 75, -25, -2, -8, -122, Byte.MIN_VALUE, 78, -103, -23, -59, -55, 24, -15, -13, 120, 88, -113, -76, 68, -47, -82, 112, 2, -97, -19, -38, 24, -6, -29, 79, 77, 53, 63, 110, -88, -124, -75, 61, 26, 106, -26, -103, 34, 90, 9, 13, 87, 21, 90, 57, 123, -68, -73, -109, 99, 105, 116, 75, -10, -2, 72, -49, -126, 26, 40, -74, -95, -74, -9, -17, -51, -63, 100, 56, 109};
        c = new byte[]{111, 111, -12, -86, 92, 91, -42, -115, 90, -80, -43, 86, 113, -32, -35, 102, -121, 48, 53, 124, 94, -93, 76, 118, -85, -110, -4, 53, 95, -10, 21, 104, -94, 55, -49, -84, -79, 107, 49, -118, 24, 98, 104, 118, -72, 104, -53, 109, -88, -94, 100, 35, -117, 28, 121, -4, 119, 11, -1, 47, 67, -59, -50, 18, 41, 94, -8, 15, 30, -4, -121, 51, -112, -111, -97, 109, -47, -63, -89, -113, -47, -82, -26, 83, 60, -18, 81, 52, 26, 111, -57, 82, -114, 50, 2, -127, -60, Byte.MAX_VALUE, 41, 63, 126, -83, 4, 21, 57, 99, 62, 86, -90, 86, -6, 78, 48, 84, -43, 18, 5, 87, 79, 51, -53, -3, 70, -80, -109, -106, -49, -15, -17, 103, -82, 17, -57, 73, -6, 11, 36, -82, -122, -35, -93, -39, Byte.MAX_VALUE, -66, -18, -122, 67, -71, -85, 78, 58, -29, 53, -95, -34, -75, 69, -120, 27, 14, -67, -90, 64, -77, 35, 38, -66, -15, -35, 49, 83, Byte.MAX_VALUE, 66, -102, -127, -89, 66, -81, -35, -115, 76, 38, 35, 99, 55, -119, -109, -2, -75, 51, -62, -95, Byte.MIN_VALUE, 38, -32, -82, 67, 90, 126, Byte.MAX_VALUE, 125, 74, 89, 65, 100, -55, 5, 47, -92, -31, 48, 3, -28, 90, -60, -79, -69, -52, -69, -23, 23, 4, -105, -67, 76, -112, 125, -95, -4, -121, 119, 119, -100, -66, -12, 9, 84, -122, 59, 16, 50, -102, 80, -117, -89, -62, -15, 43, 4, 13, -72, 96, 88, -91, 39, -76, 108, -111, 65, -99, -4, -100, 24, -60, 116, 41, -99, -67, 96, 116, 2, 69, -117, -39, -17, 50, -26, -20, 110, -21, -80, -12, -110, 117, -78, -10, -3, -44, 66, 66, -54, -102, -96, -56, 44, -86, 82, 77, 100, 73, -74, 89, -55, 52, -85, -91, 111, 12, 31, 7, -79, 121, -21, 26, -28, -109, 107, 52, 78, 40, 83, 122, -2, 122, -2, 44, -110, -122, -51, -16, 119, 43, -63, -106, 49, 77, 95, -111, -117, -53, -57, 32, -84, -65, -80, 46, 84, 7, 73, 78, -25, -100, -97, 93, -83, -24, 126, -86, 77, 11, -56, -25, 40, 103, -66, 42, 114, -26, 16, -7, 110, 121, -84, 94, -22, -11, 100, 83, 45, -92, 54, 111, 52, 61, -4, -60, -40, -91, -39, 112, -21, 83, -116, -69, -96, -104, -54, 2, -34, 111, -84, 71, -113, -36, 87, 56, -67, 110, -87, 75, -86, -115, -98, 15, 7, -3, -16, 110, -3, 108, 70, 59, 110, -90, -102, 67, -30, -26, -11, -58, 113, -34, -43, 125, -127, 73, 11, 26, -14, -4, 70, 8, -43, -73, -55, 122, 125, -38, 96, 64, -40, -115, -14, 36, 109, 65, -120, 31, -7, -72, -8, 112, -118, 107, 111, -17, -23, -35, -115, 80, -22, -111, -44, -87, -47, -55, -6, 116, -5, -103, -90, -69, 25, -93, -94, 10, 22, 9, -98, 94, -94, 104, -75, 3, -116, -72, 59, 107, 69, -109, 107, -93, -77, -17, -87, -8, -56, 126, -103, -10, 33, 3, -110, 14, 83, 62, -118, 50, 71, 15, -14, -110, -84, -79, -45, -72, -5, 97, -33, 31, 119, 37, -106, 33, -15, -42, -3, -28, 64, -19, 52, -73, 2, 69, -105, -97, 2, -112, -107, 26, 94, Byte.MAX_VALUE, -71, -91, -127, 37, -58, -114, -125, -88, 79, 17, -2, 84, -117, -107, -40, 71, 47, 60, 25, -71, -79, 73, -73, 121, 19, 38, 52, -75, 126, 17, -57, 2, -104, -125, 79, -80, 124, 79, 49, -115, 61, 10, -26, 125, -93, -122, 35, 1, 74, -12, 117, -120, 77, 97, -56, 125, -50, Byte.MIN_VALUE, 26, -111, -102, -65, 40, -38, -105, 13, 6, -87, -102, 42, -106, 60, -103, -4, 27, -39, -84, -67, 62, -76, -29, -76, 93, 12, -10, 81, -20, -9, 102, 20, 116, -40, -20, 94, 117, -122, -83, -52, -118, 40, 121, -108, -85, -63, 122, -71, -92, -84, 89, 7, 79, 61, 59, -63, 35, 96, 109, 27, 60, -68, -97, 108, 101, -65, -106, 106, -110, -55, 82, 85, 11, 79, 116, 58, -63, 95, 62, -17, -87, -91, 123, 29, 69, -16, 40, -30, 77, 67, 117, -61, 73, 74, 9, -71, 49, -101, 104, 122, 92, -45, 26, -65, 87, -121, -30, 114, -71, -114, 114, -13, Byte.MAX_VALUE, -29, 11, 52, -53, 80, -46, -93, -53, -81, 47, -69, -93, 62, -52, -105, 61, 98, 11, -23, 119, -48, 50, 29, -102, 83, 21, 45, -11, 11, -41, -116, -32, -85, -43, -45, -47, 69, -106, -116, -75, 13, 0, -123, 53, 69, -39, 76, -22, -114, 92, -4, 48, -9, -31, 66, -62, -90, -53, -17, -78, -83, 0, 75, -19, -17, -58, 6, 123, 123, 100, -16, 95, -62, 52, 49, -1, 41, 101, 95, 85, -58, 80, -43, 103, 52, 50, -68, 87, -4, 53, -69, -83, 47, -123, 83, -85, -61, -40, -115, -11, 122, 101, 102, 89, -123, -111, -126, 60, 122, -57, 78, -58, 69, -62, 22, 110, 90, -87, -2, 109, 3, 13, 27, 28, 43, 22, -109, 121, -44, -25, 93, 65, 125, -37, -47, -125, -26, -18, 50, -3, -20, -110, -7, 93, -45, 2, -68, 66, -1, 123, 68, -49, -32, 64, -62, -8, 59, -58, 51, 39, 23, -76, -45, -16, -4, -100, -12, -32, 42, 33, 104, -57, 2, -14, 115, 20, 34, -41, -121, 73, -87, 77, 103, 65, -20, -94, 88, 40, -16, 56, -49, -104, -77, 117, -71, -116, 77, -10, Byte.MIN_VALUE, -97, 14, 34, -60, -110, -73, -11, -91, -96, 49, -51, -85, -102, -62, -24, -116, 80, 49, -73, -121, -33, 19, 38, -75, -16, 99, -64, -5, -89, 126, 3, -81, -2, -124, Byte.MAX_VALUE, 114, 54, 28, -13, 56, 105, -109, 42, -4, -66, -81, -73, 100, 101, Byte.MAX_VALUE, Byte.MAX_VALUE, -82, 0, 87, -76, -48, 12, 31, -41, -28, 34, -111, -116, -37, 105, -120, -108, -88, -67, -49, 27, -36, 118, 61, 91, 23, -69, 65, 
        -65, 81, 18, -77, 103, 62, 124, 89, -81, -44, -30, -79, 90, -30, 118, 4, 10, 84, 114, 104, -60, -6, -52, 83, 104, 33, -55, -47, -94, -31, -52, -7, 95, -20, 50, -39, 124, -111, 101, -69, 87, 15, -27, 92, 49, 114, -22, -114, -59, 110, 46, 91, 45, 92, -56, 46, 112, -34, -58, -113, -69, 44, 82, -84, -104, -38, -86, -125, -96, 36, -4, 53, -52, 62, -58, -125, -58, -27, 32, 99, -14, 88, 88, -104, 44, -111, Byte.MAX_VALUE, 119, 115, 2, 95, -74, -17, 69, 79, 14, -98, 83, 13, -101, 37, -74, -73, 4, 10, -72, 118, -24, -23, -112, 92, 34, 91, 91, 19, 37, -46, -79, -55, -37, 73, 78, -4, 121, -109, -111, -4, 82, 98, -15, 29, 87, -111, -64, -119, 72, -39, 40, 112, 66, 65, -21, 43, -17, 29, 25, 122, -101, 25, 66, 99, -44, -127, -21, -47, 45, 63, 34, 84, 42, -59, Byte.MAX_VALUE, 114, -112, 91, 49, 108, -88, Byte.MAX_VALUE, 65, -20, 6, -104, 28, -122, 23, 98, 40, 95, 17, 64, 21, 31, -86, 52, 88, -73, 18, -94, -20, -2, 31, 19, -59, 21, 65, -40, 95, -106, -71, 102, 4, -113, 46, 35, -39, 94, 9, -72, -54, 45, 25, 118, 91, 113, 5, -63, 8, -127, 98, -2, -52, -102, 30, -7, -60, 90, 23, -70, -105, 106, -42, -94, -53, 115, 126, 64, -80, 101, 50, -57, -50, -27, 93, -123, 61, -50, 4, -106, 13, 97, 86, 52, 63, 22, -109, 28, -83, -102, 86, -19, 95, 60, 5, 101, 39, 23, -75, -28, -91, 24, 81, -120, -29, 23, 64, -90, 89, 59, -80, 122, -22, -6, -63, -76, -37, -8, -104, 2, 84, -54, -12, 113, -117, 106, -124, -12, -118, -3, -30, -117, 121, -38, 38, 29, 84, -61, -79, -99, -49, 25, 85, -82, 88, 70, -119, 7, 8, -115, -37, -14, 71, 100, 85, 15, -74, 86, -100, -23, -22, 69, -19, 16, -117, 99, 28, 121, 21, -54, -73, 10, -123, -9, -26, 8, -27, -84, -22, 50, 86, -18, -13, -101, 58, -98, 36, 51, -4, -119, -75, 79, -88, -35, -95, -113, -13, 1, 99, -21, 24, 26, -10, -100, 111, 124, 94, 89, 5, 5, 19, -74, -115, -47, -37, 69, 96, 104, 113, -1, -18, -10, -100, -126, -127, -19, 20, 90, 16, -108, -109, -13, 35, 117, 22, -40, 91, -90, -35, -72, 115, 125, -52, -8, -38, 70, 11, 69, -72, 8, 110, 29, -37, 86, 24, -77, 55, -54, -101, 43, -60, -118, -107, 123, 88, 80, 2, 21, -57, -93, 24, 6, 25, 31, 55, -92, 120, -8, 55, 16, 94, 15, 123, 55, -99, 102, -111, -57, 110, -95, -52, -73, -12, 91, 92, -68, 40, -86, 95, 11, 64, -115, 78, -83, 126, 36, 112, 38, 20, -115, 6, -48, -122, 54, -67, -36, 121, 111, 19, 26, -73, 94, 40, 37, -85, 81, 6, 14, -41, 90, 29, -92, -62, 120, -122, -69, 80, -85, 56, -119, 82, -63, -75, -30, 52, -33, 122, 53, -39, -40, -69, Byte.MAX_VALUE, 67, 109, 119, -121, 12, 121, -120, -27, 49, 95, 33, -110, 91, -50, 102, -83, 97, -123, -16, 2, 26, 112, -36, -37, -40, -97, -14, -64, -112, -82, -82, 95, 83, 19, 15, Byte.MAX_VALUE, -13, 3, -70, -84, 36, -36, -65, 112, 69, 36, 11, -95, 3, 43, -120, -106, -19, 28, -125, -14, -54, -117, -53, -71, -79, 126, -92, 49, 120, -15, 49, 18, 116, -122, 33, 35, 63, -68, -23, -120, -69, -59, -18, 105, 10, -94, 28, -56, 123, 11, 97, 117, -123, 4, 86, 87, 48, -37, 67, 87, -77, 15, 71, 107, -93, 21, 119, 29, -49, -120, -107, -16, 33, 78, -123, -15, 7, 79, 56, 17, -119, -28, 38, 34, -68, -35, -71, -26, -23, 125, 94, 39, -106, 39, -28, 58, 91, -17, 81, 35, -88, -22, -74, 1, -93, 112, -78, 82, 122, 42, -63, -44, -88, 91, 95, -11, -116, -44, 78, -85, -5, -30, 9, -118, 23, 63, -6, 19, 84, -16, -87, 30, 16, -59, 92, 52, -21, -102, -64, -28, -117, 96, 106, 86, -42, -63, -127, 50, -111, -62, -81, -58, 24, -101, 67};
    }

    public red(Context context) {
        this.h = 0;
        this.j = new ByteBuffer[64];
        this.q = new Object();
        this.p = context;
        acel acelVar = acel.a;
        String a2 = acelVar.b().a();
        byte[] bArr = null;
        if (a2 != null) goto L5;
        byte[] decode = null;
    L6:
        String b2 = acelVar.b().b();
        if (b2 != null) goto L9;
        byte[] decode2 = null;
    L11:
        if (d(decode2, decode) == false) goto L14;
        if (decode == null) goto L14;
        String str = new String(decode);
    L15:
        String c2 = acelVar.b().c();
        if (c2 != null) goto L18;
        byte[] decode3 = null;
    L19:
        String d = acelVar.b().d();
        if (d != null) goto L22;
        byte[] decode4 = null;
    L24:
        if (true == d(decode4, decode3)) goto L26;
        decode3 = null;
    L26:
        String e = acelVar.b().e();
        if (e != null) goto L29;
        byte[] decode5 = null;
    L30:
        String f = acelVar.b().f();
        if (f != null) goto L33;
        byte[] decode6 = null;
    L35:
        if (true != d(decode6, decode5)) goto L38;
        bArr = decode5;
    L38:
        if (str == null) goto L42;
        if (decode3 == null) goto L42;
        if (bArr == null) goto L42;
        ree reaVar = new rec(str, decode3, bArr);
    L43:
        this.i = reaVar;
        return;
    L42:
        reaVar = new rea();
        goto L43
    L33:
        decode6 = Base64.decode(f, 0);
        goto L35
    L29:
        decode5 = Base64.decode(e, 0);
        goto L30
    L22:
        decode4 = Base64.decode(d, 0);
        goto L24
    L18:
        decode3 = Base64.decode(c2, 0);
    L14:
        str = null;
        goto L15
    L9:
        decode2 = Base64.decode(b2, 0);
        goto L11
    L5:
        decode = Base64.decode(a2, 0);
        goto L6
    }

    private static boolean d(byte[] bArr, byte[] bArr2) {
        if (bArr != null) goto L5;
    L15:
        return false;
    L5:
        if (bArr.length == 0) goto L15;
        if (bArr2 == null) goto L15;
        if (bArr2.length == 0) goto L15;
        MessageDigest messageDigest = MessageDigest.getInstance("SHA-1");     // Catch: NoSuchAlgorithmException -> L16
        messageDigest.update(bArr2);     // Catch: NoSuchAlgorithmException -> L16
        if (Arrays.equals(messageDigest.digest(), bArr) == false) goto L14;
        return true;
    L14:
        a.e().ai(8329).w("Checking validity - reject");
        goto L15
    }

    private static final ByteBuffer e(ByteBuffer[] byteBufferArr, int i, int i2) {
        syl sylVar = rbk.a;
        quj.a(sylVar);
        if (i != 0) goto L6;
        quj.a(sylVar);
        return reg.a.a(0);
    L6:
        ByteBuffer a2 = reg.a.a(i2);
        int i3 = 0;
    L7:
        if (i3 >= i) goto L12;
        if (byteBufferArr[i3].hasRemaining() == false) goto L11;
        a2.put(byteBufferArr[i3]);
    L11:
        byteBufferArr[i3].clear();
        i3 = i3 + 1;
        goto L7
    L12:
        a2.position(0);
        a2.limit(i2);
        quj.a(sylVar);
        return a2;
    }

    public final ByteBuffer a(ByteBuffer byteBuffer) {
        syl sylVar = rbk.a;
        quj.a(sylVar);
        int i = this.h;
        ByteBuffer byteBuffer2 = null;
        if (i != 0) goto L7;
        a.j().ai(8311).w("Cannot do handshake before init");
        quj.a(sylVar);
        return null;
    L7:
        if (i != 3) goto L10;
        a.j().ai(8310).w("Cannot handle SSL renegotiation requests.");
        quj.a(sylVar);
        return null;
    L10:
        int i2 = 2;
        if (i != 2) goto L83;
    L17:
        int i3 = 0;
        ByteBuffer a2 = reg.a.a(0);
        int i4 = 5;
        ByteBuffer[] byteBufferArr = new ByteBuffer[5];
        boolean z = false;
        int i5 = 0;
        int i6 = 0;
        boolean z2 = false;
    L85:
        SSLEngine sSLEngine = this.l;     // Catch: Exception -> L65 Throwable -> L67
        sSLEngine.getClass();     // Catch: Exception -> L65 Throwable -> L67
        SSLEngineResult.HandshakeStatus handshakeStatus = sSLEngine.getHandshakeStatus();     // Catch: Exception -> L65 Throwable -> L67
        if (z == false) goto L21;
        int i7 = i3;
        a.d().ai(8308).A("Current status: %s", handshakeStatus);     // Catch: Exception -> L65 Throwable -> L67
    L22:
        int i8 = rdz.a[handshakeStatus.ordinal()];     // Catch: Exception -> L65 Throwable -> L67
        if (i8 == 1) goto L56;
        if (i8 == i2) goto L54;
        if (i8 == 3) goto L44;
        if (i8 == 4) goto L29;
        if (i8 == i4) goto L29;
    L51:
        int i9 = i7;
    L59:
        if (z2 == true) goto L70;
        if (this.h != 2) goto L70;
        i3 = i9;
        i2 = 2;
        i4 = 5;
    L70:
        if (a2 == null) goto L72;
        reg.a.b(a2);
    L72:
        if (i6 <= 0) goto L74;
        byteBuffer2 = e(byteBufferArr, i5, i6);
    L74:
        if (byteBuffer2 == null) goto L76;
        a.j().ai(8302).w("Phone will send SSL handshake data to car");
    L76:
        quj.a(rbk.a);
        if (z == false) goto L79;
        a.d().ai(8301).A("Final result: %s", byteBuffer2);
    L79:
        return byteBuffer2;
    L29:
        xsq xsqVar = a;     // Catch: Exception -> L65 Throwable -> L67
        xsqVar.j().ai(8306).w("Phone finished SSL handshaking");     // Catch: Exception -> L65 Throwable -> L67
        SSLEngine sSLEngine2 = this.l;     // Catch: Exception -> L65 Throwable -> L67
        sSLEngine2.getClass();     // Catch: Exception -> L65 Throwable -> L67
        X509Certificate x509Certificate = (X509Certificate) sSLEngine2.getSession().getPeerCertificates()[i7];     // Catch: Exception -> L65 Throwable -> L67
        this.d = x509Certificate.getSubjectDN().getName();     // Catch: Exception -> L65 Throwable -> L67
        BigInteger serialNumber = x509Certificate.getSerialNumber();     // Catch: Exception -> L65 Throwable -> L67
        if (serialNumber.compareTo(o) >= 0) goto L32;
        xsq xsqVar2 = xsqVar;
        this.e = serialNumber.longValue();     // Catch: Exception -> L65 Throwable -> L67
    L33:
        this.g = x509Certificate.getNotAfter().toString();     // Catch: Exception -> L65 Throwable -> L67
        this.f = x509Certificate.getNotBefore().toString();     // Catch: Exception -> L65 Throwable -> L67
        xsqVar2.d().ai(8319).A("Peer certificate subject name: %s", this.d);     // Catch: Exception -> L65 Throwable -> L67
        xsa ai = xsqVar2.d().ai(8320);     // Catch: Exception -> L65 Throwable -> L67
        long j = this.e;     // Catch: Exception -> L65 Throwable -> L67
        ai.I("Peer certificate serial number: %d (0x%x)", j, j);     // Catch: Exception -> L65 Throwable -> L67
        xsqVar2.d().ai(8321).w("Valid Times:");     // Catch: Exception -> L65 Throwable -> L67
        xsqVar2.d().ai(8322).A("    notBefore= %s", this.f);     // Catch: Exception -> L65 Throwable -> L67
        xsqVar2.d().ai(8323).A("    notAfter= %s", this.g);     // Catch: Exception -> L65 Throwable -> L67
        SSLEngine sSLEngine3 = this.l;     // Catch: Exception -> L65 Throwable -> L67
        sSLEngine3.getClass();     // Catch: Exception -> L65 Throwable -> L67
        X509Certificate x509Certificate2 = (X509Certificate) sSLEngine3.getSession().getLocalCertificates()[i7];     // Catch: Exception -> L65 Throwable -> L67
        x509Certificate2.getSubjectDN().getName();     // Catch: Exception -> L65 Throwable -> L67
        x509Certificate2.getNotBefore();     // Catch: Exception -> L65 Throwable -> L67
        x509Certificate2.getNotAfter();     // Catch: Exception -> L65 Throwable -> L67
        String str = this.d;     // Catch: Exception -> L65 Throwable -> L67
        str.getClass();     // Catch: Exception -> L65 Throwable -> L67
        if (str.contains("CarService") == true) goto L43;
        String str2 = this.d;     // Catch: Exception -> L65 Throwable -> L67
        str2.getClass();     // Catch: Exception -> L65 Throwable -> L67
        if (str2.contains("Google Automotive Link") == true) goto L41;
        this.h = 3;     // Catch: Exception -> L65 Throwable -> L67
        if (z == false) goto L51;
        xsqVar2.d().ai(8307).w("Finished handling handshake complete.");     // Catch: Exception -> L65 Throwable -> L67
        goto L51
    L41:
        throw new SSLPeerUnverifiedException("Head Unit cannot send certificate of the CA. It must send its own certificate");     // Catch: Exception -> L65 Throwable -> L67
    L43:
        throw new SSLPeerUnverifiedException("Head Unit must not use CarService certificate");     // Catch: Exception -> L65 Throwable -> L67
    L32:
        xsqVar2 = xsqVar;
        xsqVar2.f().ai(8318).A("Unable to convert serial number to long: %s", serialNumber);     // Catch: Exception -> L65 Throwable -> L67
        this.e = -1;     // Catch: Exception -> L65 Throwable -> L67
        goto L33
    L44:
        if (byteBuffer != null) goto L46;
    L86:
        a.f().ai(8305).w("Phone will wait for car to send more SSL handshake data");     // Catch: Exception -> L52 Throwable -> L67
        z = true;
        z2 = true;
    L52:
        e = e;
        z = true;
    L69:
        a.e().r(e).ai(8303).w("Error in SSL handshake");     // Catch: Throwable -> L67
        this.h = 4;     // Catch: Throwable -> L67
        goto L70
    L46:
        if (byteBuffer.hasRemaining() == false) goto L86;
        c(byteBuffer, null);     // Catch: Exception -> L65 Throwable -> L67
        goto L51
    L54:
        i9 = i7;
        ByteBuffer b2 = b(a2, i9, i9, i9);     // Catch: Exception -> L65 Throwable -> L67
        byteBufferArr[i5] = b2;     // Catch: Exception -> L65 Throwable -> L67
        i6 = i6 + b2.remaining();     // Catch: Exception -> L65 Throwable -> L67
        i5 = i5 + 1;     // Catch: Exception -> L65 Throwable -> L67
        goto L59
    L56:
        i9 = i7;
        SSLEngine sSLEngine4 = this.l;     // Catch: Exception -> L65 Throwable -> L67
        sSLEngine4.getClass();     // Catch: Exception -> L65 Throwable -> L67
        sSLEngine4.getDelegatedTask().run();     // Catch: Exception -> L65 Throwable -> L67
        if (z == false) goto L59;
        a.d().ai(8304).w("Finished running delegated task.");     // Catch: Exception -> L65 Throwable -> L67
        goto L59
    L21:
        i7 = i3;
    L65:
        e = e;
    L67:
        th = move-exception;
        if (a2 == null) goto L82;
        reg.a.b(a2);
    L82:
        throw th;
    L83:
        SSLEngine sSLEngine5 = this.l;     // Catch: SSLException -> L14
        sSLEngine5.getClass();     // Catch: SSLException -> L14
        sSLEngine5.beginHandshake();     // Catch: SSLException -> L14
        this.h = 2;     // Catch: SSLException -> L14
    L14:
        e = move-exception;
        a.e().r(e).ai(8309).w("Error beginning SSL Handshake");
        this.h = 4;
        quj.a(rbk.a);
        return null;
    }

    public final ByteBuffer b(ByteBuffer byteBuffer, int i, int i2, int i3) throws SSLException {
        quj.a(rbk.a);
        int limit = byteBuffer.limit();
        byteBuffer.position(i);     // Catch: Throwable -> L43
        byteBuffer.limit(i + i2);     // Catch: Throwable -> L43
        int i4 = 0;
        int i5 = 0;
        boolean z = false;
    L4:
        ByteBuffer[] byteBufferArr = this.j;     // Catch: Throwable -> L43
        ByteBuffer byteBuffer2 = byteBufferArr[i4];     // Catch: Throwable -> L43
        if (byteBuffer2 != null) goto L7;
        byteBuffer2 = ByteBuffer.allocateDirect(this.m);     // Catch: Throwable -> L43
        byteBufferArr[i4] = byteBuffer2;     // Catch: Throwable -> L43
    L7:
        byteBuffer2.clear();     // Catch: Throwable -> L43
        if (i4 != 0) goto L10;
        byteBufferArr[0].position(i3);     // Catch: Throwable -> L43
        i4 = 0;
    L10:
        Object obj = this.q;     // Catch: Throwable -> L43
        monitor-enter(obj);     // Catch: Throwable -> L43
        SSLEngine sSLEngine = this.l;     // Catch: Throwable -> L40
        sSLEngine.getClass();     // Catch: Throwable -> L40
        SSLEngineResult wrap = sSLEngine.wrap(byteBuffer, byteBufferArr[i4]);     // Catch: Throwable -> L40
        monitor-exit(obj);     // Catch: Throwable -> L40
        byteBufferArr[i4].flip();     // Catch: Throwable -> L43
        i5 = i5 + wrap.bytesProduced();     // Catch: Throwable -> L43
        i4 = i4 + 1;     // Catch: Throwable -> L43
        int i6 = rdz.b[wrap.getStatus().ordinal()];     // Catch: Throwable -> L43
        if (i6 != 1) goto L17;
        a.f().ai(8314).w("Buffer overflow when encrypting bytes to send");     // Catch: Throwable -> L43
    L25:
        if (z == true) goto L30;
        if (byteBuffer.hasRemaining() == false) goto L30;
        if (i4 < 64) goto L4;
    L30:
        ByteBuffer[] byteBufferArr2 = this.j;
        if (i4 != 1) goto L33;
        ByteBuffer e = byteBufferArr2[0];     // Catch: Throwable -> L43
    L34:
        quj.a(rbk.a);     // Catch: Throwable -> L43
        if (byteBuffer.hasRemaining() == false) goto L38;
        a.e().ai(8312).w("Did not encrypt all the bytes in the input!");
    L38:
        byteBuffer.limit(limit);
        return e;
    L33:
        e = e(byteBufferArr2, i4, i5);     // Catch: Throwable -> L43
        goto L34
    L17:
        if (i6 != 2) goto L19;
        a.e().ai(8315).w("Buffer underflow when encrypting bytes to send");     // Catch: Throwable -> L43
    L23:
        z = true;
        goto L25
    L19:
        if (i6 != 4) goto L25;
        a.e().ai(8316).w("SSLEngine closed when preparing bytes to send");     // Catch: Throwable -> L43
        goto L23
    L40:
        th = move-exception;
        throw th;     // Catch: Throwable -> L43
    L43:
        th = move-exception;
        if (byteBuffer.hasRemaining() == false) goto L47;
        a.e().ai(8313).w("Did not encrypt all the bytes in the input!");
    L47:
        byteBuffer.limit(limit);
        throw th;
    }

    public final void c(ByteBuffer byteBuffer, ByteBuffer byteBuffer2) throws SSLException {
        quj.a(rbk.a);
        if (byteBuffer2 != null) goto L5;
        ByteBuffer byteBuffer3 = reg.a.a(this.n);
    L6:
        int limit = byteBuffer.limit();
        int i = 0;
        boolean z = false;
    L7:
        if (byteBuffer2 == null) goto L49;
    L9:
        Object obj = this.q;     // Catch: Throwable -> L41
        monitor-enter(obj);     // Catch: Throwable -> L41
        SSLEngine sSLEngine = this.l;     // Catch: Throwable -> L38
        sSLEngine.getClass();     // Catch: Throwable -> L38
        SSLEngineResult unwrap = sSLEngine.unwrap(byteBuffer, byteBuffer3);     // Catch: Throwable -> L38
        monitor-exit(obj);     // Catch: Throwable -> L38
        i = i + 1;
        int i2 = rdz.b[unwrap.getStatus().ordinal()];     // Catch: Throwable -> L41
        if (i2 != 1) goto L17;
        a.d().ai(8298).w("Buffer overflow when decrypting bytes received");     // Catch: Throwable -> L41
        nui.i(this.p, yaq.ot);     // Catch: Throwable -> L41
    L25:
        if (z == true) goto L30;
        if (byteBuffer.hasRemaining() == false) goto L30;
        if (i < 64) goto L7;
    L30:
        if (byteBuffer2 != null) goto L32;
        reg.a.b(byteBuffer3);     // Catch: Throwable -> L41
    L32:
        quj.a(rbk.a);     // Catch: Throwable -> L41
        if (byteBuffer.hasRemaining() == false) goto L36;
        a.e().ai(8296).w("Did not decrypt all the bytes in the input buffer!");
    L36:
        byteBuffer.limit(limit);
        return;
    L17:
        if (i2 != 2) goto L19;
        a.e().ai(8299).w("Buffer underflow when decrypting bytes received");     // Catch: Throwable -> L41
        nui.i(this.p, yaq.os);     // Catch: Throwable -> L41
    L22:
        z = true;
        goto L25
    L19:
        if (i2 != 4) goto L25;
        a.e().ai(8300).w("SSLEngine closed when preparing bytes to send");     // Catch: Throwable -> L41
        goto L22
    L38:
        th = move-exception;
        throw th;     // Catch: Throwable -> L41
    L41:
        th = move-exception;
        if (byteBuffer.hasRemaining() == false) goto L45;
        a.e().ai(8297).w("Did not decrypt all the bytes in the input buffer!");
    L45:
        byteBuffer.limit(limit);
        throw th;
    L49:
        byteBuffer3.clear();     // Catch: Throwable -> L41
        goto L9
    L5:
        byteBuffer3 = byteBuffer2;
        goto L6
    }
}
