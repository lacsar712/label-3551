import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import VisitorCard from '../../components/VisitorCard'
import { mockVisitors } from '../../data/mockVisitor'
import styles from './index.module.scss'

export default function IndexPage() {
  const todayVisitors = mockVisitors.filter((item) => item.ownerName === 'owner1')

  const goDetail = (id: number) => {
    Taro.navigateTo({ url: `/pages/visitor-detail/index?id=${id}` })
  }

  return (
    <View className={styles.page}>
      <Text className={styles.title}>我的首页</Text>
      <Text className={styles.sectionTitle}>今日访客</Text>
      {todayVisitors.length > 0 ? (
        todayVisitors.map((visitor) => (
          <VisitorCard key={visitor.id} visitor={visitor} onDetail={goDetail} />
        ))
      ) : (
        <Text className={styles.empty}>今日暂无访客到访</Text>
      )}
    </View>
  )
}
