#include <iostream>
int main(){for(int p:{5,17,23}){int a=p==5?0:(p==17?2:1),b=p==5?1:(p==17?2:1),n=1;for(int x=0;x<p;++x)for(int y=0;y<p;++y)if((y*y-x*x*x-a*x-b)%p==0)++n;std::cout<<p<<' '<<a<<' '<<b<<' '<<n<<'\n';}}
