#Module-Specific definitions
%define apache_version 2.2.6
%define mod_name mod_memcached_cache
%define mod_conf B20_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	A mod_cache provider module for memcached storage
Name:		apache-%{mod_name}
Version:	0.1.0
Release:	%mkrel 12
Group:		System/Servers
License:	Apache License
URL:		http://code.google.com/p/modmemcachecache/
Source0:	http://modmemcachecache.googlecode.com/files/%{mod_name}-%{version}.tar.bz2
Source1:	%{mod_conf}
Patch0:		mod_memcached_cache-apr_memcache_linkage_fix.diff
Patch1:		mod_memcached_cache-apu13.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= %{apache_version}
Requires(pre):	apache >= %{apache_version}
Requires(pre):	apache-mod_cache >= %{apache_version}
Requires:	apache-conf >= %{apache_version}
Requires:	apache >= %{apache_version}
Requires:	apache-mod_cache >= %{apache_version}
BuildRequires:	apache-devel >= %{apache_version}
BuildRequires:	apr-util-devel >= 1.3.0
BuildRequires:	apache-source
BuildRequires:	libtool
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
This module allows your Apache 2.2.x installation to serve cached data quickly
from one or more memcached server instances rather than from your file system.
Like other caching modules available (mod_file_cache, mod_disk_cache,
mod_mem_cache, etc.) this module lets you configure some basic parameters in
your httpd.conf to enable caching based on specific criteria. Unlike the
others, mod_memcache_cache allows cached data to be shared across multiple
Apache instances.

%prep

%setup -q -n %{mod_name}-%{version}
%patch0 -p0
%patch1 -p0

cp %{SOURCE1} %{mod_conf}

cp /usr/src/apache-*/modules/cache/mod_cache.h src/

# lib64 fixes
perl -pi -e "s|/lib\ |/%{_lib}\ |g" m4/apr_memcache.m4
perl -pi -e "s|/lib/|/%{_lib}/|g" m4/apr_memcache.m4
perl -pi -e "s|/lib\b|/%{_lib}|g" m4/apr_memcache.m4

%build
rm -f configure
libtoolize --force --copy; aclocal -I m4; autoheader; automake --add-missing --copy --foreign; autoconf
rm -rf autom4te.cache

%configure2_5x --localstatedir=/var/lib \
    --with-apr-memcache=%{_prefix} \
    --with-apxs=%{_sbindir}/apxs

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%makeinstall_std AP_LIBEXECDIR=%{_libdir}/apache-extramodules

install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
        %{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README TODO
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%{_bindir}/cachetool

