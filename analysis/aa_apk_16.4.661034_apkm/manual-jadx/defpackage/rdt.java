package defpackage;

import android.content.res.Resources;
import android.os.Bundle;
import android.os.HandlerThread;
import android.os.IBinder;
import android.os.IInterface;
import android.os.Looper;
import android.os.Parcelable;
import android.os.RemoteException;
import android.util.Pair;
import com.google.android.gms.car.senderprotocol.AutoValue_Channel_FlattenedChannel;
import com.google.android.gms.car.senderprotocol.Channel;
import com.google.errorprone.annotations.ResultIgnorabilityUnspecified;
import java.io.ByteArrayOutputStream;
import java.io.Closeable;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;

/* loaded from: classes.dex */
public final class rdt {
    public static final xsq a = null;
    private static final quo i = null;
    public final rcr b;
    public final rbg c;
    public final rbx d;
    public int e;
    public rdp f;
    public rds[] g;
    final acuq h;
    private final Closeable j;
    private rbj k;
    private final quo l;
    private final int m;

    static {
        a = nui.n("CAR.GAL.GAL");
        qun a2 = quo.a();
        a2.c(false);
        i = a2.a();
    }

    public rdt(rdo rdoVar) {
        acuq acuqVar = new acuq(this);
        this.h = acuqVar;
        this.e = 0;
        rcr rcrVar = rdoVar.e;
        this.b = rcrVar;
        this.k = null;
        quo quoVar = (quo) new nbj(rdoVar.f).j(i);
        this.l = quoVar;
        this.j = rdoVar.b;
        this.g = null;
        this.c = new rbg(rdoVar.c, rcrVar, true);
        int i2 = rdoVar.p;
        this.m = i2;
        InputStream inputStream = rdoVar.g;
        OutputStream outputStream = rdoVar.j;
        xsq xsqVar = rbx.a;
        rbv rbvVar = new rbv(inputStream, outputStream);
        rbvVar.d = nwf.bw(new ijy(this, rdoVar, 9));
        rcl rclVar = rdoVar.n;
        if (rclVar == null) goto L5;
        rbvVar.i = rclVar;
    L5:
        xbn xbnVar = rdoVar.d;
        if (xbnVar == null) goto L8;
        rbvVar.h = xbnVar;
    L8:
        rbvVar.j = i2;
        rbvVar.e = rdoVar.e;
        rbvVar.l = acuqVar;
        rbvVar.f = quk.a(quoVar);
        rbvVar.g = rdoVar.c;
        this.d = new rbx(rbvVar);
        List list = rdoVar.a;
        if (list == null) goto L14;
        this.g = new rds[list.size()];
        int i3 = 0;
    L12:
        if (i3 >= rdoVar.a.size()) goto L14;
        a.d().ai(8266).A("Adding service (%s)", rbx.a((wuc) rdoVar.a.get(i3)));
        rds[] rdsVarArr = this.g;
        rds rdsVar = new rds();
        rdsVarArr[i3] = rdsVar;
        rdsVar.a = ((wuc) rdoVar.a.get(i3)).c;
        this.g[i3].b = (wuc) rdoVar.a.get(i3);
        i3 = i3 + 1;
    L14:
        rbx rbxVar = this.d;
        Channel channel = new Channel(0, -128, rex.b, rbxVar, new rbt(rbxVar, 0), rbxVar.h, rbxVar.n);
        rbxVar.b.c(channel);
        rbxVar.v.put(0, rbxVar.n);
        channel.c();
        rbxVar.h.p(channel);
        rbxVar.h.v();
        rbxVar.c[0] = channel;
        int i4 = rdoVar.l;
        if (i4 <= 0) goto L25;
        int i5 = rdoVar.i;
        if (i5 <= 0) goto L26;
        int i6 = rdoVar.h;
        if (i6 <= 0) goto L27;
        int i7 = rdoVar.m;
        if (i7 <= 0) goto L28;
        Resources resources = rdoVar.c.getResources();
        rce rceVar = this.d.g;
        rceVar.g = l(resources, i4);
        rceVar.h = l(resources, i5);
        rceVar.i = l(resources, i6);
        rceVar.f = resources.getString(i7);
        return;
    L28:
        return;
    L27:
        return;
    L26:
        return;
    }

    public static Object b(Class cls, IBinder iBinder) {
        if (iBinder != null) goto L4;
        rda rcyVar = null;
    L9:
        return cls.cast(rcz.a(rcyVar));
    L4:
        IInterface queryLocalInterface = iBinder.queryLocalInterface("com.google.android.gms.car.senderprotocol.IObjectWrapper");
        if ((queryLocalInterface instanceof rda) == false) goto L7;
        rcyVar = (rda) queryLocalInterface;
        goto L9
    L7:
        rcyVar = new rcy(iBinder);
        goto L9
    }

    static final byte[] l(Resources resources, int i2) {
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
        InputStream openRawResource = resources.openRawResource(i2);
        byte[] bArr = new byte[1024];
        int i3 = 0;
    L4:
        if (i3 == (-1)) goto L11;
        i3 = openRawResource.read(bArr);     // Catch: IOException -> L9
        if (i3 <= 0) goto L4;
        byteArrayOutputStream.write(bArr, 0, i3);     // Catch: IOException -> L9
    L9:
        a.e().ai(8269).w("Error reading raw resource.");
        goto L4
    L11:
        return byteArrayOutputStream.toByteArray();
    }

    @ResultIgnorabilityUnspecified
    public final int a(rdr rdrVar) {
        rds[] rdsVarArr = this.g;
        int length = rdsVarArr.length;
        int i2 = 0;
        int i3 = 0;
    L3:
        if (i2 >= length) goto L22;
        rds rdsVar = rdsVarArr[i2];
        if (rdsVar.d != null) goto L21;
        wuc wucVar = rdsVar.b;
        if (wucVar == null) goto L21;
        rbm a2 = rdrVar.a(wucVar);
        if (a2 == null) goto L21;
        int i4 = this.m;
        rbx rbxVar = this.d;
        rbt rbtVar = new rbt(rbxVar, rdsVar.a);
        if (i4 == 0) goto L20;
        int i5 = i4 - 1;
        if (i5 != 0) goto L15;
    L19:
        rdsVar.d = a2;
        rdsVar.b = null;
        i3 = i3 + 1;
        goto L21
    L15:
        if (i5 != 1) goto L18;
        a2 = new res(a2, rbtVar, new lwq(rbxVar.v, rbxVar.w));
        goto L19
    L18:
        throw new IllegalArgumentException("Invalid type ".concat(nui.c(i4)));
    L20:
        throw null;
    L21:
        i2 = i2 + 1;
        goto L3
    L22:
        return i3;
    }

    public final List c() {
        ArrayList arrayList = new ArrayList();
        rds[] rdsVarArr = this.g;
        int length = rdsVarArr.length;
        int i2 = 0;
    L3:
        if (i2 >= length) goto L8;
        wuc wucVar = rdsVarArr[i2].b;
        if (wucVar == null) goto L7;
        arrayList.add(wucVar.k());
    L7:
        i2 = i2 + 1;
        goto L3
    L8:
        return arrayList;
    }

    /* JADX WARN: Type inference failed for: r14v0, types: [java.lang.Object, rbn] */
    /* JADX WARN: Type inference failed for: r8v10, types: [java.lang.Object, rbm] */
    @ResultIgnorabilityUnspecified
    public final List d(rdp rdpVar) {
        if (this.f != null) goto L78;
        this.f = rdpVar;
        ArrayList arrayList = new ArrayList();
        rds[] rdsVarArr = this.g;
        int length = rdsVarArr.length;
        int i2 = 0;
    L5:
        if (i2 >= length) goto L20;
        rds rdsVar = rdsVarArr[i2];
        if (rdsVar.c != null) goto L19;
        if (rdsVar.d == null) goto L19;
        if (rdpVar.c(rdsVar.a) == false) goto L15;
        rdsVar.c = rdsVar.d.b(this.b);
    L15:
        if (rdsVar.c == null) goto L19;
        arrayList.add(rdsVar);
        rbj rbjVar = this.k;
        if (rbjVar == null) goto L19;
        int i3 = rdsVar.a;
        Object obj = rdsVar.c;
        obj.getClass();
        rbjVar.a(i3, ((rdn) obj).q);
    L19:
        i2 = i2 + 1;
        goto L5
    L20:
        this.e = arrayList.size();
        ArrayList arrayList2 = new ArrayList();
        int size = arrayList.size();
        int i4 = 0;
    L21:
        if (i4 >= size) goto L73;
        rds rdsVar2 = (rds) arrayList.get(i4);
        ?? r14 = rdsVar2.c;
        r14.getClass();
        rbx rbxVar = this.d;
        rdn rdnVar = (rdn) r14;
        rex w = rdnVar.w();
        int i5 = rdsVar2.a;
        r14.getClass();
        r14.getClass();
        int i6 = rdnVar.r;
        Object obj2 = rbxVar.d;
        monitor-enter(obj2);
        if (i6 != 2) goto L34;
        if (rbxVar.o != null) goto L29;
        rbxVar.j = new HandlerThread("RxAud", -19);     // Catch: Throwable -> L31
        rbxVar.j.start();     // Catch: Throwable -> L31
        rbxVar.o = new rbw(rbxVar, rbxVar.j.getLooper());     // Catch: Throwable -> L31
    L29:
        rbw rbwVar = rbxVar.o;     // Catch: Throwable -> L31
    L30:
        rbw rbwVar2 = rbwVar;
    L47:
        rbxVar.v.put(Integer.valueOf(i5), rbwVar2);     // Catch: Throwable -> L31
        Object obj3 = obj2;
        ArrayList arrayList3 = arrayList;
        Channel channel = new Channel(i5, 0, w, rbxVar, new rbt(rbxVar, i5), r14, rbwVar2);     // Catch: Throwable -> L71
        rbxVar.c[i5] = channel;     // Catch: Throwable -> L71
        ((rdn) r14).p(channel);     // Catch: Throwable -> L71
        rbxVar.b.c(channel);     // Catch: Throwable -> L71
        ram b = ram.b(((rdn) r14).q);     // Catch: Throwable -> L71
        b.getClass();     // Catch: Throwable -> L71
        rbxVar.t.g(i5, ntz.i(b));     // Catch: Throwable -> L71
        rbxVar.b(i5, a.P(b));     // Catch: Throwable -> L71
        Object obj4 = channel.k;     // Catch: Throwable -> L71
        monitor-enter(obj4);     // Catch: Throwable -> L71
    L66:
        th = move-exception;
        throw th;     // Catch: Throwable -> L71
    L52:
        if (channel.h != 4) goto L65;
        channel.h = 0;     // Catch: Throwable -> L66
        monitor-exit(obj4);     // Catch: Throwable -> L66
        if (rbxVar.e == true) goto L58;
        if (i6 == 3) goto L58;
    L59:
        monitor-exit(obj3);     // Catch: Throwable -> L71
        arrayList2.add(Integer.valueOf(rdsVar2.a));
        Object obj5 = rdsVar2.c;
        obj5.getClass();
        if (rdpVar.b(((rdn) obj5).q) == false) goto L63;
        a.j().ai(8271).y("Starter requests to force open service %d.", rdsVar2.a);
        channel.c();
        Object obj6 = rdsVar2.c;
        obj6.getClass();
        ((rdn) obj6).v();
    L63:
        i4 = i4 + 1;
        arrayList = arrayList3;
    L58:
        channel.b();     // Catch: Throwable -> L71
        goto L59
    L65:
        throw new IllegalStateException("Channel needs to be closed before it can be opened.");     // Catch: Throwable -> L66
    L71:
        th = th;
    L69:
        monitor-exit(obj3);     // Catch: Throwable -> L71
        throw th;
    L31:
        th = th;
        obj3 = obj2;
        goto L69
    L34:
        if (i6 != 1) goto L40;
        if (rbxVar.p != null) goto L38;
        rbxVar.l = new HandlerThread("RxVid", -8);     // Catch: Throwable -> L31
        rbxVar.l.start();     // Catch: Throwable -> L31
        rbxVar.p = new rbw(rbxVar, rbxVar.l.getLooper());     // Catch: Throwable -> L31
    L38:
        rbwVar = rbxVar.p;     // Catch: Throwable -> L31
        goto L30
    L40:
        if (i6 == 3) goto L42;
        rbw rbwVar3 = rbxVar.n;     // Catch: Throwable -> L31
    L46:
        rbwVar2 = rbwVar3;
        goto L47
    L42:
        if (rbxVar.q != null) goto L44;
        rbxVar.m = new HandlerThread("RxSen");     // Catch: Throwable -> L31
        rbxVar.m.start();     // Catch: Throwable -> L31
        rbxVar.q = new rbw(rbxVar, rbxVar.m.getLooper());     // Catch: Throwable -> L31
    L44:
        rbwVar3 = rbxVar.q;     // Catch: Throwable -> L31
        goto L46
    L73:
        ArrayList arrayList4 = arrayList;
        a.j().ai(8270).y("%d car services started.", arrayList4.size());
        if (arrayList4.isEmpty() == false) goto L76;
        this.f = null;
        rdpVar.a();
    L76:
        return arrayList2;
    L78:
        throw new IllegalStateException("Can't start services while waiting on services");
    }

    public final void e() {
        rbg rbgVar = this.c;
        Object obj = rbgVar.f;
        monitor-enter(obj);
        rbgVar.i = true;     // Catch: Throwable -> L11
        rbgVar.a();     // Catch: Throwable -> L11
        monitor-exit(obj);     // Catch: Throwable -> L11
        this.d.c(false);
        Closeable closeable = this.j;
        if (closeable == null) goto L19;
        closeable.close();     // Catch: IOException -> L14
        return;
    L20:
        return;
    L19:
        return;
    L11:
        th = move-exception;
        throw th;
    }

    public final void f() {
        this.d.f();
        rds[] rdsVarArr = this.g;
        if (rdsVarArr == null) goto L11;
        int i2 = 0;
    L6:
        if (i2 >= rdsVarArr.length) goto L15;
        Object obj = rdsVarArr[i2].c;
        if (obj == null) goto L10;
        ((rdn) obj).h();
    L10:
        i2 = i2 + 1;
        goto L6
    L15:
        return;
    }

    public final void g(wof wofVar) {
        rbg rbgVar = this.c;
        Object obj = rbgVar.f;
        monitor-enter(obj);
    L15:
        th = move-exception;
        throw th;
    L5:
        if (rbgVar.i == false) goto L9;
        rbg.a.d().ai(8155).w("Ignoring byebye on released handler");     // Catch: Throwable -> L15
        monitor-exit(obj);     // Catch: Throwable -> L15
        return;
    L9:
        rbgVar.g = new sbn(Looper.getMainLooper());     // Catch: Throwable -> L15
        rbgVar.h = new qvg(rbgVar, 15, null);     // Catch: Throwable -> L15
        rbgVar.g.postDelayed(rbgVar.h, 200);     // Catch: Throwable -> L15
        monitor-exit(obj);     // Catch: Throwable -> L15
        rbgVar.d = true;
        rcd rcdVar = rbgVar.b;
        if (rcdVar == null) goto L19;
        rcdVar.a(wofVar);
        return;
    }

    public final void h(rbj rbjVar) {
        this.k = rbjVar;
        rbx rbxVar = this.d;
        rbxVar.s = rbjVar;
        rbxVar.b.e(rbjVar);
        if (rbjVar == null) goto L12;
        int i2 = 0;
        rbjVar.a(0, 1);
        rds[] rdsVarArr = this.g;
        if (rdsVarArr != null) goto L7;
        return;
    L7:
        if (i2 >= rdsVarArr.length) goto L17;
        rds rdsVar = rdsVarArr[i2];
        Object obj = rdsVar.c;
        if (obj == null) goto L11;
        rbjVar.a(rdsVar.a, ((rdn) obj).q);
    L11:
        i2 = i2 + 1;
        goto L7
    L17:
        return;
    }

    public final void i() {
        a.j().ai(8272).w("startServiceDiscovery");
        final rbx rbxVar = this.d;
        rbxVar.b.g();
        final int i2 = 1;
        rcs rcsVar = new rbs(rbxVar, i2);
        final int i3 = 0;
        rcs rcsVar2 = new rbs(rbxVar, i3);
        qxf qxfVar = rbxVar.x;
        ((rct) qxfVar.a).b(rcsVar);
        ((rct) qxfVar.b).b(rcsVar2);
    }

    /* JADX WARN: Type inference failed for: r5v9, types: [java.lang.Object, rfq] */
    public final void j(Bundle bundle) {
        rdp rdpVar = this.f;
        if (rdpVar != null) goto L71;
        int i2 = 0;
        int i3 = 0;
    L5:
        rds[] rdsVarArr = this.g;
        if (i3 >= rdsVarArr.length) goto L37;
        Object obj = rdsVarArr[i3].d;
        if (obj == null) goto L28;
        if ((obj instanceof rny) == false) goto L36;
        rny rnyVar = (rny) obj;
        Object obj2 = rnyVar.a;
        monitor-enter(obj2);
        rdy rdyVar = rnyVar.e;     // Catch: Throwable -> L32
        monitor-exit(obj2);     // Catch: Throwable -> L32
        if (rnyVar.d == true) goto L19;
        rdyVar.k(wub.m, -1);
    L19:
        Object obj3 = rnyVar.b;
        monitor-enter(obj3);
        ArrayList arrayList = new ArrayList(rnyVar.c);     // Catch: Throwable -> L29
        monitor-exit(obj3);     // Catch: Throwable -> L29
        int size = arrayList.size();
        int i4 = 0;
    L24:
        if (i4 >= size) goto L28;
        ((wlm) arrayList.get(i4)).a.c();     // Catch: RemoteException -> L72
    L27:
        i4 = i4 + 1;
    L29:
        th = move-exception;
        throw th;
    L32:
        th = move-exception;
        throw th;
    L36:
        throw new UnsupportedOperationException("Non-suspendable service ".concat(obj.toString()));
    L28:
        i3 = i3 + 1;
        goto L5
    L37:
        rbx rbxVar = this.d;
        rcj rcjVar = rbxVar.b;
        rcjVar.h();
        rbx.g(rbxVar.i);
        rbx.g(rbxVar.j);
        HandlerThread handlerThread = rbxVar.k;
        rbx.g(rbxVar.m);
        rbx.g(rbxVar.l);
        if (rbxVar.f == true) goto L69;
        if (rbxVar.e == true) goto L69;
        int length = rbxVar.c.length;
        Channel.FlattenedChannel[] flattenedChannelArr = new Channel.FlattenedChannel[256];
        int i5 = 0;
    L42:
        Channel[] channelArr = rbxVar.c;
        int length2 = channelArr.length;
        if (i5 >= 256) goto L57;
        Channel channel = channelArr[i5];
        if (channel == null) goto L56;
        int i6 = channel.h;
        if (i6 == 4) goto L52;
        if (i6 != 2) goto L55;
        i6 = 2;
    L55:
        throw new IllegalStateException("Can't flatten channel: " + i6 + " " + channel.i);
    L52:
        if (channel.i == true) goto L55;
        flattenedChannelArr[i5] = new AutoValue_Channel_FlattenedChannel(channel.b, channel.e, i6, channel.f);
    L56:
        i5 = i5 + 1;
        goto L42
    L57:
        bundle.putParcelableArray("channels", flattenedChannelArr);
        rbxVar.h.g(bundle);
        rcjVar.a(bundle);
        bundle.putBinder("connection", new rcz(this.j));
        ArrayList arrayList2 = new ArrayList();
        ArrayList<? extends Parcelable> arrayList3 = new ArrayList();
        rds[] rdsVarArr2 = this.g;
        int length3 = rdsVarArr2.length;
    L58:
        if (i2 >= length3) goto L66;
        rds rdsVar = rdsVarArr2[i2];
        if (rdsVar.b == null) goto L63;
        arrayList2.add(new Pair(Integer.valueOf(rdsVar.a), rdsVar.b.k()));
    L65:
        i2 = i2 + 1;
        goto L58
    L63:
        if (rdsVar.c == null) goto L65;
        Bundle bundle2 = new Bundle();
        bundle2.putInt("end_point_service_id", rdsVar.a);
        Object obj4 = rdsVar.c;
        obj4.getClass();
        ((rdn) obj4).g(bundle2);
        arrayList3.add(bundle2);
        goto L65
    L66:
        bundle.putBinder("proto_services", new rcz(arrayList2));
        bundle.putParcelableArrayList("end_points", arrayList3);
        return;
    L69:
        throw new IllegalStateException("Can't bundle ChannelManager:" + rbxVar.f + " " + rbxVar.e);
    L71:
        throw new IllegalStateException("Can't suspend ProtocolManager:".concat(rdpVar.toString()));
    }

    public final boolean k() {
        return this.d.g.o.C(new rdu(1, 4));
    }
}
