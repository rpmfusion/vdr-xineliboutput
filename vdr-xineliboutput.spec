%global xinever %(xine-config --version  2>/dev/null || echo ERROR)
%global xineplugindir %(xine-config --plugindir  2>/dev/null || echo ERROR)
%global xinepluginver 2.0.0
%global pname   xineliboutput
%global vdrver  %(vdr-config --version 2>/dev/null || echo ERROR)
%global cvsver  20140429
# build bluray support (disabled for now)
%global have_bluray 1

Name:           vdr-%{pname}
Version:        1.1.0
Release:        10%{?cvsver:.cvs%{cvsver}}%{?dist}
Summary:        Plugins for watching VDR over Xine

Group:          Applications/Multimedia
License:        GPLv2+
URL:            http://sourceforge.net/projects/xineliboutput
# how to get the tarball
# cvs -d:pserver:anonymous@xineliboutput.cvs.sourceforge.net:/cvsroot/xineliboutput co vdr-xineliboutput
# mv vdr-xineliboutput vdr-xineliboutput-1.1.0-20140429
# tar cfz /home/martin/rpmbuild/SOURCES/vdr-xineliboutput-1.1.0-20140429.tgz vdr-xineliboutput-1.1.0-20140429
Source0:        %{name}-%{version}%{?cvsver:-%{cvsver}}.tgz
Source1:        %{name}.conf
Source2:        allowed_hosts.conf

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
BuildRequires:  mesa-libGL-devel
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

%description
VDR plugin: xine-lib based software output device for VDR

This package contain plugin for Xine

%package plugin
Summary:        Plugins for watching VDR over Xine
Group:          Applications/Multimedia
License:        GPLv2+
Requires:       %{name}%{?_isa} = %{version}-%{release}
Provides:       libxineliboutput-fbfe.so = %{version}
Provides:       libxineliboutput-sxfe.so = %{version}

%description plugin
VDR plugin: xine-lib based software output device for VDR

This package contain plugin for VDR

%prep
%setup -q -n %{name}-%{version}%{?cvsver:-%{cvsver}}

./configure \
    --enable-x11 \
    --enable-fb \
    --enable-vdr \
    --enable-libxine  \
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

make install DESTDIR=%{buildroot}

install -pm 755 mpg2c %{buildroot}%{_bindir}/mpg2c
ln -s %{vdr_plugindir}/libxineliboutput-fbfe.so.%{xinepluginver}-cvs \
      %{buildroot}%{vdr_plugindir}/libxineliboutput-fbfe.so.%{xinepluginver}
ln -s %{vdr_plugindir}/libxineliboutput-sxfe.so.%{xinepluginver}-cvs \
      %{buildroot}%{vdr_plugindir}/libxineliboutput-sxfe.so.%{xinepluginver}
install -pm 644 black_720x576.mpg %{buildroot}%{_sysconfdir}/vdr/plugins/%{pname}
install -pm 644 nosignal_720x576.mpg %{buildroot}%{_sysconfdir}/vdr/plugins/%{pname}
install -pm 644 vdrlogo_720x576.mpg %{buildroot}%{_sysconfdir}/vdr/plugins/%{pname}
ln -s nosignal_720x576.mpg %{buildroot}%{_sysconfdir}/vdr/plugins/%{pname}/nosignal.mpg


# fix debug symbols extraction / stripping
find %{buildroot}%{xineplugindir} -name '*.so' -exec chmod +x '{}' ';'

%find_lang %{name}

%files -f %{name}.lang
%doc COPYING HISTORY README*
%{_bindir}/vdr-fbfe
%{_bindir}/vdr-sxfe
%{_bindir}/mpg2c

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
%{vdr_plugindir}/libxineliboutput-fbfe.so.%{xinepluginver}-cvs
%{vdr_plugindir}/libxineliboutput-sxfe.so.%{xinepluginver}
%{vdr_plugindir}/libxineliboutput-sxfe.so.%{xinepluginver}-cvs


%changelog
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
