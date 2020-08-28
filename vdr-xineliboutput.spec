%global xinever %(pkg-config --modversion libxine  2>/dev/null || echo ERROR)
%global xineplugindir %(pkg-config --variable=plugindir libxine  2>/dev/null || echo ERROR)
%global xinepluginver 2.2.0
%global pname   xineliboutput
%global vdrver  %(pkg-config --modversion vdr 2>/dev/null || echo ERROR)
%global gitrev  43e9fa7
%global gitdate 20200702
# build bluray support (disabled for now)
%global have_bluray 1
%global have_wayland 1

Name:           vdr-%{pname}
Version:        2.2.0
Release:        3.%{gitdate}git%{gitrev}%{?dist}
Summary:        Plugins for watching VDR over Xine
License:        GPLv2+
URL:            http://sourceforge.net/projects/xineliboutput
# checkout instructions
# git clone https://git.code.sf.net/p/xineliboutput/git vdr-xineliboutput
# cd vdr-xineliboutput
# git rev-parse --short HEAD
# git archive --format=tar.gz --prefix=vdr-xineliboutput/ %%{gitrev} \
#     -o vdr-xineliboutput-%%{version}-%%{gitrev}.tar.gz
Source0:        %{name}-%{version}-%{gitrev}.tar.gz
Source1:        %{name}.conf
Source2:        allowed_hosts.conf
Patch0:         fix_build_libglvnd.patch

BuildRequires:  gcc-c++
BuildRequires:  gettext
BuildRequires:  vdr-devel >= %{vdrver}
BuildRequires:  libextractor-devel >= 0.5.22
BuildRequires:  xine-lib-devel >= 1.1.9
BuildRequires:  libvdpau-devel >= 0.4.1
BuildRequires:  libX11-devel >= 1.3.4
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libXinerama-devel
BuildRequires:  libXrender-devel
BuildRequires:  libcap-devel
BuildRequires:  dbus-glib-devel
BuildRequires:  freeglut-devel
BuildRequires:  pkgconfig(gl)
BuildRequires:  mesa-libGLU-devel
BuildRequires:  libXext-devel
BuildRequires:  xorg-x11-proto-devel
BuildRequires:  ffmpeg-devel

Requires:       vdr(abi)%{?_isa} = %{vdr_apiversion}
Requires:       libextractor >= 0.5.22
Requires:       xine-lib >= %{xinever}

%if %{have_bluray}
BuildRequires:  libbluray-devel
%endif

%if %{have_wayland}
BuildRequires:  wayland-devel
%endif

%description
VDR plugin: xine-lib based software output device for VDR

This package contain plugin for Xine

%package plugin
Summary:        Plugins for watching VDR over Xine
License:        GPLv2+
Requires:       %{name}%{?_isa} = %{version}-%{release}
Provides:       libxineliboutput-fbfe.so = %{version}
Provides:       libxineliboutput-sxfe.so = %{version}

%description plugin
VDR plugin: xine-lib based software output device for VDR

This package contain plugin for VDR

%prep
%setup -q -n %{name}
#%%patch0 -p1

./configure \
    --enable-x11 \
    --enable-fb \
    --enable-vdr \
    --enable-libxine \
%if %{have_wayland}
    --enable-wayland \
%endif
    --debug \
%if !%{have_bluray}
    --disable-libbluray \
%endif
    VDRDIR=%{vdr_plugindir} \
    VDRINCDIR=%{_includedir} \
    LOCALEDIR=./locale \
    XINELIBOUTPUT_FB=1 \
    XINELIBOUTPUT_X11=1 \
    XINELIBOUTPUT_VDRPLUGIN=1 \
    XINELIBOUTPUT_XINEPLUGIN=1

%build
FFMPEG_CFLAGS="$FFMPEG_CFLAGS $(${cross_prefix}pkg-config --cflags libavformat libavcodec libswscale libavutil)"
export=FFMPEG_CFLAGS 
make CFLAGS="%{optflags} -fPIC $FFMPEG_CFLAGS" CXXFLAGS="%{optflags} -fPIC $FFMPEG_CFLAGS" %{?_smp_mflags} all

%install
install -dm 755 %{buildroot}%{xineplugindir}
install -dm 755 %{buildroot}%{xineplugindir}/post
install -dm 755 %{buildroot}%{vdr_plugindir}
install -dm 755 %{buildroot}%{_bindir}
install -dm 755 %{buildroot}%{_sysconfdir}/sysconfig/vdr-plugins.d
install -dm 755 %{buildroot}%{_sysconfdir}/vdr/plugins/%{pname}
install -dm 755 %{buildroot}%{_datadir}/vdr/xineliboutput
install -pm 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/sysconfig/vdr-plugins.d/xineliboutput.conf
install -pm 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/vdr/plugins/%{pname}/

%make_install

install -pm 755 mpg2c %{buildroot}%{_bindir}/mpg2c
#ln -s %%{vdr_plugindir}/libxineliboutput-fbfe.so.%%{xinepluginver}-git \
#      %%{buildroot}%{vdr_plugindir}/libxineliboutput-fbfe.so.%%{xinepluginver}
#ln -s %%{vdr_plugindir}/libxineliboutput-sxfe.so.%%{xinepluginver}-git \
#      %%{buildroot}%%{vdr_plugindir}/libxineliboutput-sxfe.so.%%{xinepluginver}
install -pm 644 black_720x576.mpg %{buildroot}%{_sysconfdir}/vdr/plugins/%{pname}
install -pm 644 nosignal_720x576.mpg %{buildroot}%{_sysconfdir}/vdr/plugins/%{pname}
install -pm 644 vdrlogo_720x576.mpg %{buildroot}%{_sysconfdir}/vdr/plugins/%{pname}
ln -s nosignal_720x576.mpg %{buildroot}%{_sysconfdir}/vdr/plugins/%{pname}/nosignal.mpg


# fix debug symbols extraction / stripping
find %{buildroot}%{xineplugindir} -name '*.so' -exec chmod +x '{}' ';'

%find_lang %{name}

%files -f %{name}.lang
%doc HISTORY README*
%license COPYING
%{_bindir}/vdr-fbfe
%{_bindir}/vdr-sxfe
%{_bindir}/mpg2c
%if %{have_wayland}
%{_bindir}/vdr-wlfe
%endif

%{xineplugindir}/xineplug_inp_xvdr.so
%{xineplugindir}/post/xineplug_post_audiochannel.so
%{xineplugindir}/post/xineplug_post_autocrop.so
%{xineplugindir}/post/xineplug_post_swscale.so
%{vdr_configdir}/plugins/%{pname}/

%files plugin
%dir %{vdr_configdir}/plugins/%{pname}
%config(noreplace) %{_sysconfdir}/sysconfig/vdr-plugins.d/%{pname}.conf
%config(noreplace) %{_sysconfdir}/vdr/plugins/%{pname}/allowed_hosts.conf

%{vdr_plugindir}/libvdr-%{pname}.so.%{vdr_apiversion}
%{vdr_plugindir}/libxineliboutput-fbfe.so.%{xinepluginver}
%{vdr_plugindir}/libxineliboutput-sxfe.so.%{xinepluginver}
%if %{have_wayland}
%{vdr_plugindir}/libxineliboutput-wlfe.so.%{xinepluginver}
%endif

%changelog
* Fri Aug 28 2020 Martin Gansser <martinkg@fedoraproject.org> - 2.2.0-3.20200702git43e9fa7
- Rebuilt for new VDR API version

* Tue Aug 18 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.2.0-2.20200702git43e9fa7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Sun Jul 12 2020 Martin Gansser <martinkg@fedoraproject.org> - 2.2.0-1.20200702git43e9fa7
- Update to 2.2.0-1.20200702git43e9fa7

* Sat Jul 11 2020 Leigh Scott <leigh123linux@gmail.com> - 2.1.0-19.20191117git32a5ffc
- Rebuilt

* Wed Feb 05 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.1.0-18.20191117git32a5ffc
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Sun Dec 15 2019 Leigh Scott <leigh123linux@gmail.com> - 2.1.0-17.20191117git32a5ffc
- Fix build issue building against libglvnd headers

* Thu Dec 12 2019 Martin Gansser <martinkg@fedoraproject.org> - 2.1.0-16.20191117git32a5ffc
- Update to 2.1.0-16.20191117git32a5ffc

* Fri Aug 09 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.1.0-15.20190607git021d0fc
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Mon Jul 01 2019 Martin Gansser <martinkg@fedoraproject.org> - 2.1.0-14.20190618git021d0fc
- Rebuilt for new VDR API version 2.4.1

* Tue Jun 18 2019 Martin Gansser <martinkg@fedoraproject.org> - 2.1.0-13.20190618git021d0fc
- Update to 2.1.0-13.20190618git021d0fc
- Rebuilt for new VDR API version

* Wed May 22 2019 Martin Gansser <martinkg@fedoraproject.org> - 2.1.0-12.20190519gitc91fae0
- Update to 2.1.0-12.20190519gitc91fae0

* Thu May 16 2019 Martin Gansser <martinkg@fedoraproject.org> - 2.1.0-11.20190514git22d2fb4
- Update to 2.1.0-11.20190516git22d2fb4
- Enable wayland support

* Tue Mar 05 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.1.0-10.20181005gitb298178
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Oct 12 2018 Martin Gansser <martinkg@fedoraproject.org> - 2.1.0-9.20181005gitb298178
- Update to 2.1.0-9.20181005gitb298178
- Add BR gcc-c++

* Sun Aug 19 2018 Leigh Scott <leigh123linux@googlemail.com> - 2.1.0-8.20180701git97b7e78
- Rebuilt for Fedora 29 Mass Rebuild binutils issue

* Sat Jul 28 2018 Martin Gansser <martinkg@fedoraproject.org> - 2.1.0-7.20180701git97b7e78
- Update to 2.1.0-7.20180701git97b7e78

* Fri Jul 27 2018 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.1.0-6.20180226git747f03e
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Apr 18 2018 Martin Gansser <martinkg@fedoraproject.org> - 2.1.0-5.20180226git747f03e
- Rebuilt for vdr-2.4.0

* Sat Mar 10 2018 Martin Gansser <martinkg@fedoraproject.org> - 2.1.0-4.20180226git747f03e
- Update to 2.1.0-4.20180226git747f03e

* Thu Mar 08 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 2.1.0-3.20180118gitcdd6595
- Rebuilt for new ffmpeg snapshot

* Thu Mar 01 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 2.1.0-2.20180118gitcdd6595
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Jan 18 2018 Martin Gansser <martinkg@fedoraproject.org> - 2.1.0-1.20180118gitcdd6595
- Update to 2.1.0-1.20180118gitcdd6595

* Thu Dec 28 2017 Martin Gansser <martinkg@fedoraproject.org> - 2.0.0-1.20171207gitf397e7e
- Update to 2.0.0-1.20171207gitf397e7e

* Thu Aug 31 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 1.1.0-24.20170315git46f0f1d
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sun Apr 30 2017 Leigh Scott <leigh123linux@googlemail.com> - 1.1.0-23.20170315git46f0f1d
- Rebuild for ffmpeg update

* Sat Apr 08 2017 Martin Gansser <martinkg@fedoraproject.org> - 1.1.0-22.20170315git46f0f1d
- Update for xinepluginver 2.0.1
- Update to recent git version fix (rfbz#4504)

* Mon Mar 20 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 1.1.0-21.20170213git71eefbe
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Feb 15 2017 Martin Gansser <martinkg@fedoraproject.org> - 1.1.0-20.20170213git71eefbe
- Update to recent git version

* Sat Jan 28 2017 Martin Gansser <martinkg@fedoraproject.org> - 1.1.0-19.20160607git29f7afd
- Update to recent git version

* Sat Jul 30 2016 Julian Sikorski <belegdol@fedoraproject.org> - 1.1.0-18.20160508git9027ea1
- Rebuilt for ffmpeg-3.1.1

* Sat Jul 02 2016 Martin Gansser <martinkg@fedoraproject.org> - 1.1.0-17.20160508git9027ea1
- Update to recent git version
- Switched checkout command to git

* Wed Apr 22 2015 Martin Gansser <martinkg@fedoraproject.org> - 1.1.0-16.cvs20150422
- Update to recent cvs version

- Added patch %%{pname}_renamed_iDoubleTapTimeoutMs_in_libcec.diff
* Tue Mar 03 2015 Martin Gansser <martinkg@fedoraproject.org> - 1.1.0-15.cvs20150220
- mark license files as %%license where available

* Tue Mar 03 2015 Martin Gansser <martinkg@fedoraproject.org> - 1.1.0-14.cvs20150220
- Update to recent cvs version
- Added patch %%{pname}_renamed_iDoubleTapTimeoutMs_in_libcec.diff

* Mon Oct 20 2014 Sérgio Basto <sergio@serjux.com> - 1.1.0-13.cvs20140704
- Rebuilt for FFmpeg 2.4.3

* Thu Aug 07 2014 Sérgio Basto <sergio@serjux.com> - 1.1.0-12.cvs20140704
- Rebuilt for ffmpeg-2.3

* Fri Jul 04 2014 Martin Gansser <martinkg@fedoraproject.org> - 1.1.0-11.cvs20140704
- Update to recent cvs version

* Thu May 29 2014 Martin Gansser <martinkg@fedoraproject.org> - 1.1.0-10.cvs20140429
- added %%dir %%{vdr_configdir}/plugins/%%{pname} to file section 

* Wed May 28 2014 Martin Gansser <martinkg@fedoraproject.org> - 1.1.0-9.cvs20140429
- added %%{vdr_configdir}/plugins/%%{pname} to file section because not owned
- Use %%global instead of %%define

* Wed May 28 2014 Martin Gansser <martinkg@fedoraproject.org> - 1.1.0-8.cvs20140429
- dropped LIBDIR option in configure section
- removed DESTDIR=%%{buildroot}
- removed  macro %%defattr in file plugin section
- removed  configure flag DESTDIR
- removed %%{vdr_configdir} in file section already owned by the vdr package
- changed Requires tag in package plugins to %%{name}%%{?_isa} = %%{version}-%%{release}
- added Requires vdr to main package

* Wed May 28 2014 Martin Gansser <martinkg@fedoraproject.org> - 1.1.0-7.cvs20140429
- added global macro xinepluginver
- corrected Source url

* Tue May 27 2014 Martin Gansser <martinkg@fedoraproject.org> - 1.1.0-6.cvs20140429
- removed hardcoded ffmpeg CFLAGS option from configure
- added FFMPEG_CFLAGS build flag
- corrected link to xineplugins because of rpmlint warning W: dangling-relative-symlink

* Mon May 26 2014 Martin Gansser <martinkg@fedoraproject.org> - 1.1.0-5.cvs20140429
- removed unused libdir path
- replaced hardlink path in CFLAGS by macro
- removed %%dir %%{vdr_plugindir} already owned by vdr/vdr-devel
- removed macro %%defattr from file section
- removed extra flag for building cvs build

* Mon May 26 2014 Martin Gansser <martinkg@fedoraproject.org> - 1.1.0-4.cvs20140429
- Drop libbluray requires which rpmlint reports as error E: explicit-lib-dependency libbluray
- Drop libvdpau requires which rpmlint reports as error E: explicit-lib-dependency libvdpau

* Sun May 25 2014 Martin Gansser <martinkg@fedoraproject.org> - 1.1.0-3.cvs20140429
- changed hardlink into macros
- changed release tag
- Use %%global instead of %%define

* Sun May 25 2014 Martin Gansser <martinkg@fedoraproject.org> - 1.1.0-2.xine.1.2.5.vdr.2.0.5.cvs20140429
- Update to recent cvs version

 Fri May 23 2014 Martin Gansser <martinkg@fedoraproject.org> - 1.1.0-1.xine.1.2.5.vdr.2.0.5
- Update to 1.1.0
- added CFLAGS and CXXFLAGS optflags
- specfile cleanup

* Fri Aug 17 2012 Zoran Pericic <zpericic@netst.org> - 1.0.90-27.xine.1.2.2.vdr.1.7.27.cvs20120817
- update to cvs 20120817
- xine-lib 1.2.2

* Sun Jun 12 2011 Zoran Pericic <zpericic@netst.org> - 1.0.90-18.1.7.18.cvs20110611
- xinelib 1.2
- separate VDR plugin in separate subpackage
- add bluray support (disabled for now)

* Fri Jan 25 2008 Zoran Pericic <zpericic@inet.hr> - 1.0.3-2.0
- xinelib 1.1.15-3
- fedora 10

* Fri Jan 25 2008 Zoran Pericic <zpericic@inet.hr> - 1.0.0-rc2.6
- libs fix

* Fri Jan 25 2008 Zoran Pericic <zpericic@inet.hr> - 1.0.0-rc2.6
- install script fix
- install vdr files

* Fri Jan 25 2008 Zoran Pericic <zpericic@inet.hr> - 1.0.0-rc2.6
- new xine-lib 1.1.9.1
- install script fix
- added i18n files

* Mon Dec 17 2007 Zoran Pericic <zpericic@inet.hr> - 1.0.0-rc2.3
- apiversion

* Mon Dec 17 2007 Zoran Pericic <zpericic@inet.hr> - 1.0.0-rc2.2
- Config file and specs changelog rework

* Mon Dec 17 2007 Zoran Pericic <zpericic@inet.hr> - 1.0.0-rc2.1
- Added config file

* Mon Dec 17 2007 Zoran Pericic <zpericic@inet.hr> - 1.0.0-rc2
- Initial build
