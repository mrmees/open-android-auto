package defpackage;

import android.content.Context;
import android.os.SystemClock;
import j$.util.Objects;
import java.io.IOException;
import java.io.InputStream;
import java.net.SocketException;
import java.net.SocketTimeoutException;
import java.nio.ByteBuffer;
import java.nio.channels.WritableByteChannel;

/* loaded from: classes2.dex */
final class rcn extends Thread {
    public volatile boolean a;
    public final Object b;
    public WritableByteChannel c;
    public rcx d;
    private final Context e;
    private final InputStream f;
    private final byte[] g;
    private final ByteBuffer h;
    private final boolean i;
    private final int j;
    private boolean k;

    public rcn(Context context, InputStream inputStream, rcl rclVar) {
        super("ReaderThread");
        byte[] bArr = new byte[16384];
        this.g = bArr;
        this.a = true;
        this.b = new Object();
        this.k = false;
        this.f = inputStream;
        ByteBuffer wrap = ByteBuffer.wrap(bArr);
        this.h = wrap;
        wrap.limit(0);
        this.i = true;
        this.e = context;
        this.j = rclVar.e;
        if (context != null) goto L6;
        rcq.a.f().ai(8208).w("Context is null, can't publish connection events.");
        return;
    }

    @Override // java.lang.Thread, java.lang.Runnable
    public final void run() {
        rcq.a.j().ai(8209).w("ReaderThread: started");
    L142:
    L88:
        th = move-exception;
        monitor-enter(this.b);
    L133:
        th = move-exception;
        throw th;
    L126:
        if (this.c != null) goto L138;
    L131:
        throw th;
    L138:
        rcq.a.j().ai(8217).w("ReaderThread: closing the channel");     // Catch: IOException -> L129 Throwable -> L133
        this.c.close();     // Catch: IOException -> L129 Throwable -> L133
    L129:
        e = move-exception;
        rcq.a.f().r(e).ai(8218).w("Impossible");     // Catch: Throwable -> L133
    L90:
        e = move-exception;
        xsq xsqVar = rcq.a;     // Catch: Throwable -> L88
        xsqVar.f().r(e).ai(8219).w("ReaderThread: crashing with exception");     // Catch: Throwable -> L88
        Context context = this.e;     // Catch: Throwable -> L88
        if (context == null) goto L95;
        nui.i(context, yaq.kG);     // Catch: Throwable -> L88
    L95:
        monitor-enter(this.b);
    L104:
        th = move-exception;
        throw th;
    L97:
        if (this.c != null) goto L152;
    L102:
    L118:
        rcq.a.j().ai(8210).w("ReaderThread: finished");
        return;
    L152:
        xsqVar.j().ai(8220).w("ReaderThread: closing the channel");     // Catch: IOException -> L100 Throwable -> L104
        this.c.close();     // Catch: IOException -> L100 Throwable -> L104
    L100:
        e = move-exception;
        rcq.a.f().r(e).ai(8221).w("Impossible");     // Catch: Throwable -> L104
    L107:
        e = move-exception;
        rcq.a.f().r(e).ai(8214).w("IOException with byte channel!!!");     // Catch: Throwable -> L88
        monitor-enter(this.b);
    L120:
        th = move-exception;
        throw th;
    L112:
        if (this.c != null) goto L146;
    L117:
        goto L118
    L146:
        rcq.a.j().ai(8215).w("ReaderThread: closing the channel");     // Catch: IOException -> L115 Throwable -> L120
        this.c.close();     // Catch: IOException -> L115 Throwable -> L120
    L115:
        e = move-exception;
        rcq.a.f().r(e).ai(8216).w("Impossible");     // Catch: Throwable -> L120
        goto L117
    L4:
        if (this.a == false) goto L75;
        Object obj = this.b;     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        monitor-enter(obj);     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
    L143:
        boolean z = false;
        if (this.c != null) goto L17;
        if (this.a == false) goto L17;
        obj.wait();     // Catch: InterruptedException -> L13 Throwable -> L72
    L13:
        Thread.currentThread().interrupt();     // Catch: Throwable -> L72
        this.a = false;     // Catch: Throwable -> L72
        rcq.a.d().ai(8223).w("ReaderThread: interrupted");     // Catch: Throwable -> L72
        Context context2 = this.e;     // Catch: Throwable -> L72
        if (context2 == null) goto L143;
        nui.i(context2, yaq.kF);     // Catch: Throwable -> L72
    L17:
        if (this.a == false) goto L18;
        WritableByteChannel writableByteChannel = this.c;     // Catch: Throwable -> L72
        ByteBuffer byteBuffer = this.h;     // Catch: Throwable -> L72
        int write = writableByteChannel.write(byteBuffer);     // Catch: Throwable -> L72
        if (write < 0) goto L22;
        monitor-exit(obj);     // Catch: Throwable -> L72
        boolean z2 = true;
        InputStream inputStream = this.f;     // Catch: IOException -> L46 Throwable -> L88 Exception -> L90
        byte[] bArr = this.g;     // Catch: IOException -> L46 Throwable -> L88 Exception -> L90
        if (true != this.i) goto L30;
        write = 16384;
    L30:
        int read = inputStream.read(bArr, 0, write);     // Catch: IOException -> L46 Throwable -> L88 Exception -> L90
        rcx rcxVar = this.d;     // Catch: IOException -> L46 Throwable -> L88 Exception -> L90
        if (rcxVar == null) goto L33;
        rcxVar.e(SystemClock.elapsedRealtime(), read);     // Catch: IOException -> L46 Throwable -> L88 Exception -> L90
    L33:
        if (read >= 0) goto L34;
        xsa ai = rcq.a.f().ai(8213);     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        boolean z3 = this.k;     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        if (this.j == 2) goto L39;
        z2 = false;
    L39:
        ai.R("ReaderThread: end of stream received, dataReceived=%b, isWireless=%b", z3, z2);     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        this.a = false;     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        Context context3 = this.e;     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        if (context3 == null) goto L142;
        if (this.k == false) goto L44;
        yaq yaqVar = yaq.kD;     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
    L45:
        nui.i(context3, yaqVar);     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        goto L142
    L44:
        yaqVar = yaq.kE;     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        goto L45
    L34:
        this.k = true;     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        byteBuffer.limit(read);     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
    L46:
        e = move-exception;
        xsa ai2 = rcq.a.f().r(e).ai(8222);     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        boolean z4 = this.k;     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        if (this.j != 2) goto L50;
        z = true;
    L50:
        ai2.R("IO exception, dataReceived=%b, isWireless=%b", z4, z);     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        if (this.k == true) goto L55;
        Context context4 = this.e;     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        if (context4 == null) goto L55;
        nui.i(context4, yaq.kx);     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
    L55:
        Context context5 = this.e;     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        if (context5 == null) goto L75;
        nui.i(context5, yaq.ky);     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        if ((e instanceof SocketTimeoutException) == false) goto L61;
        nui.i(context5, yaq.kz);     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        goto L75
    L61:
        if ((e instanceof SocketException) == false) goto L75;
        if (Objects.equals(e.getMessage(), "Software caused connection abort") == false) goto L66;
        nui.i(context5, yaq.kC);     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        goto L75
    L66:
        if (Objects.equals(e.getMessage(), "Connection reset") == false) goto L69;
        nui.i(context5, yaq.kB);     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        goto L75
    L69:
        if (Objects.equals(e.getMessage(), "Socket closed") == false) goto L75;
        nui.i(context5, yaq.kA);     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
        goto L75
    L22:
        monitor-exit(obj);     // Catch: Throwable -> L72
        goto L75
    L18:
        monitor-exit(obj);     // Catch: Throwable -> L72
    L72:
        th = move-exception;
        throw th;     // Catch: Throwable -> L88 Exception -> L90 IOException -> L107
    L75:
        Object obj2 = this.b;
        monitor-enter(obj2);
    L85:
        th = move-exception;
        throw th;
    L78:
        if (this.c != null) goto L150;
    L83:
        monitor-exit(obj2);     // Catch: Throwable -> L85
        goto L118
    L150:
        rcq.a.j().ai(8211).w("ReaderThread: closing the channel");     // Catch: IOException -> L81 Throwable -> L85
        this.c.close();     // Catch: IOException -> L81 Throwable -> L85
    L81:
        e = move-exception;
        rcq.a.f().r(e).ai(8212).w("Impossible");     // Catch: Throwable -> L85
        goto L83
    }
}
