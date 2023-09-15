%define	bitlbid	bitlbee

Summary:	IRC proxy to connect to ICQ, AOL, MSN and Jabber
Name:		bitlbee
Version:	3.6
Release:	1
License:	GPLv2+
Group:		Networking/Instant messaging
Url:		http://bitlbee.org/
Source0:	http://get.bitlbee.org/src/%{name}-%{version}.tar.gz
# When the above patches will  be consolidated upstream, this should merge
# with Patch1 or Patch2 or something like that
Patch5:		bitlbee-forkdaemon.patch
# Patch rejected upstream, however we need to keep this, because
# of the SELinux policy is set up for this mode of operation.
Patch6:		bitlbee-systemd.patch
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(gnutls)
BuildRequires:	pkgconfig(libgcrypt)
BuildRequires:	pkgconfig(libsoup-2.4)
BuildRequires:	pkgconfig(systemd)
BuildRequires:	rpm-helper
Requires(post):	ccp
Requires(pre,post,preun):	rpm-helper

%description
%{name} is a proxy which accepts connections from any irc-client
and allows you to communicate using following instant messaging
protocols:
 - ICQ
 - AIM
 - MSN
 - YIM
 - Jabber (including Google Talk and Facebook)
 - Twitter

%files
%defattr(0750,root,%{bitlbid},0755)
%{_sbindir}/%{name}
%defattr(0644,root,root,0755)
%doc doc/AUTHORS doc/README doc/FAQ
%doc doc/CHANGES doc/CREDITS
%doc doc/user-guide/
%{_datadir}/%{name}/help.txt
%dir %{_datadir}/%{name}/
%{_mandir}/man?/*
%config(noreplace) %{_sysconfdir}/%{name}/motd.txt
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%{_unitdir}/%{name}*
%defattr(0600,%{bitlbid},%{bitlbid},0700)
%{_var}/lib/%{name}

%pre
%_pre_useradd %{bitlbid} %{_var}/%{name} /bin/true
# in post it is harder to know if the new empty dir already exists
if [ $1 = 2 -a -d "%{_var}/%{name}" -a ! -d "%{_var}/lib/%{name}" ]; then
   echo -n " NOTE: new location of bitlbee users data: "
   mv -v "%{_var}/%{name}" "%{_var}/lib/%{name}"
fi

%post
ccp --delete --ifexists --set NoOrphans --oldfile %{_sysconfdir}/%{name}/%{name}.conf --newfile %{_sysconfdir}/%{name}/%{name}.conf.rpmnew
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

#----------------------------------------------------------------------------

%prep
%setup -q
%autopatch -p1
# Use the nick "bitlbee" instead of "root"
sed -i 's/ROOT_NICK "root"/ROOT_NICK "bitlbee"/' bitlbee.h

%build
perl -pi -e "s#CFLAGS=\"-O2#CFLAGS=\"%{optflags}#g" configure
./configure	--prefix=%{_prefix} \
		--etcdir=%{_sysconfdir}/%{name} \
		--libdir=%{_libdir}/%{name} \
		--sbindir=%{_sbindir} \
		--strip=0 \
		--otr=0

%make

%install
%makeinstall_std install-etc
install -d %{buildroot}%{_var}/lib/%{name}

install -p -d %{buildroot}%{_unitdir}
install -p -m 644 init/%{name}{.service,@.service,.socket} %{buildroot}%{_unitdir}

