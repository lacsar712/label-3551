import { View, Text } from '@tarojs/components'
import Taro, { useRouter } from '@tarojs/taro'
import { mockVisitors } from '../../data/mockVisitor'
import styles from './index.module.scss'

export default function VisitorDetailPage() {
  const router = useRouter()
  const visitor = mockVisitors.find((item) => String(item.id) === router.params.id)

  if (!visitor) {
    return (
      <View className={styles.page}>
        <Text className={styles.empty}>未找到访客信息</Text>
      </View>
    )
  }

  return (
    <View className={styles.page}>
      <Text className={styles.title}>访客详情</Text>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>访客基本信息</Text>
        <View className={styles.row}><Text className={styles.label}>访客姓名</Text><Text className={styles.value}>{visitor.name}</Text></View>
        <View className={styles.row}><Text className={styles.label}>联系电话</Text><Text className={styles.value}>{visitor.phone}</Text></View>
        <View className={styles.row}><Text className={styles.label}>身份证后四位</Text><Text className={styles.value}>{visitor.idCardLast4}</Text></View>
        <View className={styles.row}><Text className={styles.label}>来访事由</Text><Text className={styles.value}>{visitor.visitReason}</Text></View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>拜访信息</Text>
        <View className={styles.row}><Text className={styles.label}>拜访业主</Text><Text className={styles.value}>{visitor.ownerName}</Text></View>
        <View className={styles.row}><Text className={styles.label}>关联房号</Text><Text className={styles.value}>{visitor.unitName}</Text></View>
        <View className={styles.row}><Text className={styles.label}>登记人</Text><Text className={styles.value}>{visitor.registerStaff || '-'}</Text></View>
        <View className={styles.row}><Text className={styles.label}>登记时间</Text><Text className={styles.value}>{visitor.registerTime}</Text></View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>时间信息</Text>
        <View className={styles.row}><Text className={styles.label}>预计停留时长</Text><Text className={styles.value}>{visitor.estimatedDuration} 分钟</Text></View>
        <View className={styles.row}><Text className={styles.label}>预计离开时间</Text><Text className={styles.value}>{visitor.estimatedLeaveTime}</Text></View>
        <View className={styles.row}><Text className={styles.label}>实际离开时间</Text><Text className={styles.value}>{visitor.actualLeaveTime || '-'}</Text></View>
        <View className={styles.row}>
          <Text className={styles.label}>当前状态</Text>
          <Text className={visitor.status === 'visiting' ? styles.statusActive : styles.statusLeft}>
            {visitor.status === 'visiting' ? '在访' : '已离场'}
          </Text>
        </View>
      </View>
    </View>
  )
}
