package defpackage;

import android.os.RemoteException;
import android.os.SystemClock;
import android.util.ArrayMap;
import android.util.SparseArray;
import com.google.android.gms.car.senderprotocol.ChannelMessage;
import java.io.BufferedOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.util.Iterator;

/* loaded from: classes2.dex */
final class rcp {
    public final boolean a;
    public final OutputStream b;
    final /* synthetic */ rcq c;
    private final ByteBuffer d;
    private byte[] e;

    public rcp(rcq rcqVar, OutputStream outputStream, int i) {
        this.c = rcqVar;
        this.d = ByteBuffer.allocate(8);
        this.e = new byte[8];
        this.b = new BufferedOutputStream(outputStream, i);
        this.a = true;
    }

    final void a(ChannelMessage channelMessage, boolean z) throws IOException {
        syl sylVar = rbk.a;
        quj.a(sylVar);
        syl sylVar2 = rcq.j;
        if (quj.a(sylVar2) == false) goto L5;
        long j = SystemClock.elapsedRealtime();
    L6:
        int i = channelMessage.a;
        if (channelMessage.e == true) goto L9;
    L11:
        boolean z2 = false;
    L12:
        int i2 = channelMessage.d;
        boolean z3 = true;
        long j2 = 0;
    L13:
        if (i >= i2) goto L112;
        if (i != 0) goto L16;
        int i3 = 1;
    L17:
        int i4 = 8;
        int i5 = 4;
        if (i3 == 0) goto L21;
        if (z2 == false) goto L21;
        int i6 = 8;
    L22:
        rcq rcqVar = this.c;
        int min = Math.min(i2 - i, rcqVar.h - i6);
        if (z2 == true) goto L25;
    L28:
        syl sylVar3 = sylVar;
        boolean z4 = true;
        boolean z5 = true;
    L29:
        if (z4 == z5) goto L31;
        int i7 = 0;
    L32:
        int i8 = i3 | i7;
        syl sylVar4 = sylVar2;
        if (z4 == channelMessage.f) goto L35;
        i5 = 0;
    L35:
        boolean z6 = channelMessage.h;
        if (z4 == z6) goto L38;
        i4 = 0;
    L38:
        ByteBuffer byteBuffer = channelMessage.c;
        int arrayOffset = i + byteBuffer.arrayOffset();
        if (z6 == false) goto L45;
        boolean z7 = z6;
        red redVar = rcqVar.e;
        if (redVar == null) goto L44;
        int i9 = i + min;
        byteBuffer = redVar.b(byteBuffer, i, min, i6);
        int i10 = byteBuffer.remaining();
        min = i10 - i6;
        int i11 = byteBuffer.arrayOffset();
    L46:
        long j3 = j;
        int i12 = (i8 | i5) | i4;
        ByteBuffer byteBuffer2 = this.d;
        byteBuffer2.clear();
        byteBuffer2.limit(i6);
        boolean z8 = z2;
        int i13 = channelMessage.b;
        boolean z9 = z5;
        byteBuffer2.put((byte) (i13 & 255));
        byteBuffer2.put((byte) i12);
        byteBuffer2.putShort((short) min);
        if (i3 == 0) goto L50;
        if (z8 == false) goto L50;
        byteBuffer2.putInt(i2);
    L50:
        rbj rbjVar = rcqVar.f;
        if (rbjVar == null) goto L75;
        Object obj = ((rbi) rbjVar).b;
        monitor-enter(obj);
        int i14 = min;
        int i15 = ((rbi) rbjVar).g.get(i13, -1);     // Catch: Throwable -> L71
        SparseArray sparseArray = ((rbi) rbjVar).d;     // Catch: Throwable -> L71
        if (sparseArray.get(i15) == null) goto L68;
        long currentTimeMillis = System.currentTimeMillis();     // Catch: Throwable -> L71
        Iterator it = ((ArrayMap) sparseArray.get(i15)).keySet().iterator();     // Catch: Throwable -> L71
    L59:
        if (it.hasNext() == false) goto L68;
        int i16 = i15;
        int i17 = i13;
        ((rbh) it.next()).b.h(currentTimeMillis, i17, i16, i12, i14);     // Catch: RemoteException -> L126 Throwable -> L71
    L67:
        i14 = i14;
        i13 = i17;
        i15 = i16;
    L65:
        i16 = i15;
        i17 = i13;
    L68:
        min = i14;
        monitor-exit(obj);     // Catch: Throwable -> L71
    L71:
        th = move-exception;
        throw th;
    L75:
        if (quj.a(sylVar4) == false) goto L77;
        long j4 = SystemClock.elapsedRealtime();
    L78:
        if (z7 == false) goto L81;
        byteBuffer2.flip();
        byteBuffer.put(byteBuffer2);
        int i18 = byteBuffer.arrayOffset();
        byte[] bArr = byteBuffer.array();
        long j5 = j4;
    L84:
        OutputStream outputStream = this.b;
        outputStream.write(bArr, i18, i10);
        if (this.a == false) goto L88;
        if (z == false) goto L88;
        outputStream.flush();
    L88:
        acuq acuqVar = rcqVar.l;
        SystemClock.elapsedRealtime();
        Object obj2 = acuqVar.a;
        rbj rbjVar2 = rcqVar.f;
        if (rbjVar2 == null) goto L100;
        Object obj3 = ((rbi) rbjVar2).b;
        long elapsedRealtime = SystemClock.elapsedRealtime();
        monitor-enter(obj3);
        rbh rbhVar = ((rbi) rbjVar2).e;     // Catch: Throwable -> L97
        if (rbhVar != null) goto L132;
    L95:
        monitor-exit(obj3);     // Catch: Throwable -> L97
        goto L100
    L132:
        rbhVar.b.f(elapsedRealtime, i10);     // Catch: RemoteException -> L127 Throwable -> L97
    L97:
        th = move-exception;
        throw th;
    L100:
        if (z7 == false) goto L106;
        if (byteBuffer == rcqVar.e.j[0]) goto L106;
        reg.a.b(byteBuffer);
    L106:
        if (quj.a(sylVar4) == false) goto L109;
        j2 = j2 + (SystemClock.elapsedRealtime() - j5);
    L109:
        if (rcqVar.k != null) goto L110;
        z2 = z8;
        z3 = z9;
        sylVar = sylVar3;
        sylVar2 = sylVar4;
        i = i9;
        j = j3;
        goto L13
    L110:
        z3 = z9;
    L113:
        if (z3 == false) goto L116;
        reg.a.b(channelMessage.c);
    L116:
        if (quj.a(sylVar4) == false) goto L120;
        long elapsedRealtime2 = SystemClock.elapsedRealtime() - j3;
        if (elapsedRealtime2 <= 10) goto L120;
        rcq.a.j().ai(8228).S("sendMessage total delay %d transport %d size %d", Long.valueOf(elapsedRealtime2), Long.valueOf(j2), Integer.valueOf(i2));
    L120:
        quj.a(sylVar3);
        if (z3 == false) goto L144;
        int i19 = channelMessage.i;
        if (i19 == 0) goto L145;
        rcq rcqVar2 = this.c;
        ((rbx) rcqVar2.l.a).e(channelMessage.b, i19);
        return;
    L145:
        return;
    L144:
        return;
    L81:
        if (this.e.length >= i10) goto L83;
        this.e = new byte[i10];
    L83:
        j5 = j4;
        System.arraycopy(byteBuffer2.array(), byteBuffer2.arrayOffset(), this.e, 0, i6);
        System.arraycopy(byteBuffer.array(), i11, this.e, i6, min);
        bArr = this.e;
        i18 = 0;
        goto L84
    L77:
        j4 = 0;
        goto L78
    L44:
        throw new IllegalStateException("Cannot send an encrypted frame with no ssl context.");
    L45:
        z7 = z6;
        i10 = i6 + min;
        i9 = i + min;
        i11 = arrayOffset;
        goto L46
    L31:
        i7 = 2;
        goto L32
    L25:
        if ((i + min) >= i2) goto L28;
        sylVar3 = sylVar;
        z4 = true;
        z5 = false;
    L21:
        i6 = 4;
        goto L22
    L16:
        i3 = 0;
        goto L17
    L112:
        sylVar3 = sylVar;
        sylVar4 = sylVar2;
        j3 = j;
        goto L113
    L9:
        if (channelMessage.d <= (this.c.h - 4)) goto L11;
        z2 = true;
        goto L12
    L5:
        j = 0;
        goto L6
    }

    public rcp(rcq rcqVar, OutputStream outputStream) {
        this.c = rcqVar;
        this.d = ByteBuffer.allocate(8);
        this.e = new byte[8];
        this.b = outputStream;
        this.a = false;
    }
}
