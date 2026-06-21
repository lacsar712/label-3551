import { View, Text, Input } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useState } from 'react'
import styles from './index.module.scss'

export default function VisitorAddPage() {
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [idCardLast4, setIdCardLast4] = useState('')
  const [visitReason, setVisitReason] = useState('')

  const handleSubmit = () => {
    if (!name || !phone || !idCardLast4 || !visitReason) {
      Taro.showToast({ title: '请填写完整信息', icon: 'none' })
      return
    }
    Taro.showToast({ title: '访客登记成功', icon: 'success' })
    setTimeout(() => Taro.navigateBack(), 800)
  }

  return (
    <View className={styles.page}>
      <Text className={styles.title}>访客登记</Text>
      <View className={styles.form}>
        <View className={styles.field}>
          <Text className={styles.label}>访客姓名</Text>
          <Input className={styles.input} value={name} onInput={(e) => setName(e.detail.value)} placeholder="请输入访客姓名" />
        </View>
        <View className={styles.field}>
          <Text className={styles.label}>联系电话</Text>
          <Input className={styles.input} value={phone} onInput={(e) => setPhone(e.detail.value)} placeholder="请输入联系电话" />
        </View>
        <View className={styles.field}>
          <Text className={styles.label}>身份证后四位</Text>
          <Input className={styles.input} value={idCardLast4} maxlength={4} onInput={(e) => setIdCardLast4(e.detail.value)} placeholder="请输入后四位" />
        </View>
        <View className={styles.field}>
          <Text className={styles.label}>来访事由</Text>
          <Input className={styles.input} value={visitReason} onInput={(e) => setVisitReason(e.detail.value)} placeholder="请输入来访事由" />
        </View>
        <Text className={styles.submit} onClick={handleSubmit}>提交登记</Text>
      </View>
    </View>
  )
}
