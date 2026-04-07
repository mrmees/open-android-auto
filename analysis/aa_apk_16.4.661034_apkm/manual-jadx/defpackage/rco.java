package defpackage;

import android.os.RemoteException;
import android.os.SystemClock;
import android.util.ArrayMap;
import android.util.SparseArray;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.WritableByteChannel;
import java.util.Iterator;
import java.util.concurrent.TimeUnit;

/* loaded from: classes2.dex */
final class rco implements WritableByteChannel {
    public final ByteBuffer[] a;
    public final ByteBuffer b;
    public final ByteBuffer c;
    public int d;
    public int e;
    public int f;
    public byte g;
    public int h;
    public boolean i;
    final /* synthetic */ rcq j;
    private boolean k;
    private boolean l;
    private final acuq m;

    public rco(rcq rcqVar, acuq acuqVar) {
        this.j = rcqVar;
        this.m = acuqVar;
        this.a = new ByteBuffer[256];
        this.b = ByteBuffer.allocate(8);
        this.c = ByteBuffer.allocate(16384);
    }

    private static final boolean a(int i, int i2) {
        if ((i & i2) == 0) goto L6;
        return true;
    L6:
        return false;
    }

    @Override // java.nio.channels.Channel, java.io.Closeable, java.lang.AutoCloseable
    public final void close() throws IOException {
        rcq rcqVar = this.j;
        if (rcqVar.c.getAndSet(false) == false) goto L6;
        rcqVar.l.d(yco.aa);
        return;
    }

    @Override // java.nio.channels.Channel
    public final boolean isOpen() {
        throw new UnsupportedOperationException();
    }

    @Override // java.nio.channels.WritableByteChannel
    public final int write(ByteBuffer byteBuffer) {
        if (this.d == 3) goto L134;
        int i = 4;
    L114:
        e = move-exception;
        rcq.a.f().r(e).ai(8227).w("Receiver:");
        this.d = 3;
        rcq rcqVar = this.j;
        rcqVar.c.set(false);
        if ((e instanceof rch) == false) goto L121;
        acuq acuqVar = rcqVar.l;
        rbx.a.f().ai(8179).w("Framing Error encountered.");
        Object obj = acuqVar.a;
        ByteBuffer a = reg.a.a(2);
        a.putShort(-1);
        rbx rbxVar = (rbx) obj;
        rbxVar.h(0, a, false, false, new rby(false, false, 0));
        rbxVar.c(true);
    L124:
        int i2 = this.d;
        if (i2 == 0) goto L127;
        if (i2 == 1) goto L130;
        if (i2 != 2) goto L134;
        return this.h;
    L130:
        return 8 - this.b.position();
    L127:
        return 4 - this.b.position();
    L121:
        if ((e instanceof OutOfMemoryError) == false) goto L123;
        rcqVar.l.d(yco.as);
        goto L124
    L123:
        rcqVar.l.d(yco.ac);
        goto L124
    L7:
        if (byteBuffer.limit() <= 0) goto L9;
        acuq acuqVar2 = this.j.l;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        SystemClock.elapsedRealtime();     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        Object obj2 = acuqVar2.a;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
    L9:
        byte[] array = byteBuffer.array();     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        int limit = byteBuffer.limit();     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        int i3 = 0;
        int i4 = 0;
    L10:
        i3 = i3 + i4;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        if (i3 >= limit) goto L124;
        int i5 = this.d;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        int i6 = limit - i3;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        if (i5 != 0) goto L42;
        ByteBuffer byteBuffer2 = this.b;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        int min = Math.min(4 - byteBuffer2.position(), i6);     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        byteBuffer2.put(array, i3, min);     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        if (byteBuffer2.position() != i) goto L41;
        byteBuffer2.rewind();     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        this.e = byteBuffer2.get() & 255;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        byte b = byteBuffer2.get();     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        this.g = b;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        this.k = a(b, 8);     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        this.l = a(b, 2);     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        char c = (char) byteBuffer2.getShort();     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        this.f = c;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        this.h = c;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        rbj rbjVar = this.j.f;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        if (rbjVar == null) goto L38;
        int i7 = this.e;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        byte b2 = this.g;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        Object obj3 = ((rbi) rbjVar).b;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        monitor-enter(obj3);     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        int i8 = ((rbi) rbjVar).g.get(i7, -1);     // Catch: Throwable -> L34
        SparseArray sparseArray = ((rbi) rbjVar).d;     // Catch: Throwable -> L34
        if (sparseArray.get(i8) == null) goto L32;
        long currentTimeMillis = System.currentTimeMillis();     // Catch: Throwable -> L34
        Iterator it = ((ArrayMap) sparseArray.get(i8)).keySet().iterator();     // Catch: Throwable -> L34
    L24:
        if (it.hasNext() == false) goto L32;
        byte b3 = b2;
        int i9 = i8;
        char c2 = c;
        ((rbh) it.next()).b.g(currentTimeMillis, i7, i9, b3, c2);     // Catch: RemoteException -> L135 Throwable -> L34
    L31:
        i8 = i9;
        b2 = b3;
        c = c2;
    L30:
        b3 = b2;
        i9 = i8;
        c2 = c;
    L32:
        monitor-exit(obj3);     // Catch: Throwable -> L34
    L34:
        th = move-exception;
        throw th;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
    L38:
        if (a(this.g, 1) == false) goto L40;
        this.d = 1;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        goto L41
    L40:
        this.d = 2;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        byteBuffer2.clear();     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
    L41:
        i4 = min;
    L111:
        i = 4;
        goto L10
    L42:
        if (i5 == 1) goto L44;
        if (i5 != 2) goto L110;
        ByteBuffer byteBuffer3 = this.a[this.e];     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        if (byteBuffer3 == null) goto L109;
        if (this.k == false) goto L84;
        rcq rcqVar2 = this.j;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        if (rcqVar2.e != null) goto L74;
        if (this.i == true) goto L74;
        rcq.a.d().ai(8226).ac(this.e, this.g);     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        rcqVar2.d.tryAcquire(250, TimeUnit.MILLISECONDS);     // Catch: InterruptedException -> L136 OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
    L69:
        if (this.j.e != null) goto L71;
        boolean z = true;
    L72:
        this.i = z;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        goto L74
    L71:
        z = false;
    L74:
        if (this.i == false) goto L78;
        i4 = Math.min(this.h, i6);     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        int i10 = this.h - i4;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        this.h = i10;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        if (i10 != 0) goto L111;
        rcq.a.d().ai(8225).S("Ignoring encrypted frame with no ssl: %d %d 0x%X", Integer.valueOf(this.f), Integer.valueOf(this.e), Byte.valueOf(this.g));     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
    L88:
        if (this.l == false) goto L104;
        if (this.j.c.get() == false) goto L102;
        int position = byteBuffer3.position();     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        int limit2 = byteBuffer3.limit();     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        byteBuffer3.rewind();     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        if (this.i == true) goto L94;
    L96:
        if (position != limit2) goto L100;
        acuq acuqVar3 = this.m;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        ((rbx) acuqVar3.a).d(this.e, byteBuffer3, a(this.g, 4));     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
    L98:
        this.a[this.e] = null;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
    L105:
        this.d = 0;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        goto L111
    L100:
        throw new rch("Fragment underflow");     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
    L94:
        if (this.k == false) goto L96;
        rcq.a.d().ai(8224).w("Encrypted frame with no ssl, skipping message");     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        this.i = false;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        goto L98
    L102:
        throw new IOException("should stop");     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
    L104:
        if (byteBuffer3.position() < byteBuffer3.limit()) goto L105;
        throw new rch("Fragment overflow");     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
    L78:
        int i11 = this.f;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        ByteBuffer byteBuffer4 = this.c;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        i4 = Math.min(i11 - byteBuffer4.position(), i6);     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        byteBuffer4.put(array, i3, i4);     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        if (byteBuffer4.position() != this.f) goto L111;
        byteBuffer4.flip();     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        this.j.e.c(byteBuffer4, byteBuffer3);     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        if (this.l == false) goto L83;
        byteBuffer3.limit(byteBuffer3.position());     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
    L83:
        byteBuffer4.clear();     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        goto L88
    L84:
        i4 = Math.min(this.h, i6);     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        byteBuffer3.put(array, i3, i4);     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        int i12 = this.h - i4;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        this.h = i12;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        if (i12 == 0) goto L88;
    L109:
        throw new rch("Unexpected continuation fragment");     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
    L110:
        i4 = 0;
        goto L111
    L44:
        if (a(this.g, 2) == false) goto L46;
        int i13 = this.f;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        i4 = 0;
    L49:
        if (i13 < 0) goto L56;
        ByteBuffer[] byteBufferArr = this.a;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        if (byteBufferArr[this.e] != null) goto L54;
        this.b.clear();     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        byteBufferArr[this.e] = reg.a.a(i13);     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        byteBufferArr[this.e].limit(i13);     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        this.d = 2;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        goto L111
    L54:
        throw new rch("Received duplicate first fragment");     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
    L56:
        throw new rch(a.di(i13, "Wrong size: "));     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
    L46:
        ByteBuffer byteBuffer5 = this.b;     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        i4 = Math.min(byteBuffer5.remaining(), i6);     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        byteBuffer5.put(array, i3, i4);     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        if (byteBuffer5.position() != 8) goto L111;
        byteBuffer5.position(4);     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
        i13 = byteBuffer5.getInt();     // Catch: OutOfMemoryError -> L112 Throwable -> L114 rch -> L116
    L134:
        return -1;
    }
}
