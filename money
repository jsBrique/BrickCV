#include<iostream>
using namespace std;


int moneys(float sum,float five_index,float weight1=1,float weight2=2,float weight3=5)//根据5分数量计算组合次数
{
	return (int)((sum/weight2)-(weight3/weight2)*five_index)+1;//离散三角形法

}
int main()
{

	int sum=0,i=0,s=0;
	for(i=0;i<=20;i++)//遍历所有5分的情况
	{
		s=moneys(100,i);
		system("pause");
		cout<<"有"<<i<<"张5分时的组合数"<<s<<endl; 
		sum=sum+s;
	}
	cout<<"共有"<<sum<<"换法"<<endl;
	system("pause");
	return 0;
}
